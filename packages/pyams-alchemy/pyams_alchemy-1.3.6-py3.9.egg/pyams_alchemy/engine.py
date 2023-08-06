#
# Copyright (c) 2015-2021 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_alchemy.engine module

This module defines main SQLAlchemy integration features.
"""

import logging
import time
from datetime import datetime
from threading import Lock, Thread

from persistent import Persistent
from persistent.mapping import PersistentMapping
from pyramid.events import subscriber
from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool, Pool
from zope.container.contained import Contained
from zope.lifecycleevent import IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent
from zope.schema.fieldproperty import FieldProperty
from zope.sqlalchemy import register
from zope.sqlalchemy.datamanager import STATUS_ACTIVE, STATUS_READONLY, _SESSION_STATE, \
    join_transaction

from pyams_alchemy.interfaces import ALCHEMY_ENGINES_VOCABULARY, IAlchemyEngineUtility, \
    MANAGE_SQL_ENGINES_PERMISSION, REQUEST_SESSION_KEY
from pyams_security.interfaces import IViewContextPermissionChecker
from pyams_site.interfaces import ISiteRoot
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config
from pyams_utils.registry import query_utility
from pyams_utils.request import check_request, get_request_data, set_request_data
from pyams_utils.traversing import get_parent
from pyams_utils.vocabulary import LocalUtilitiesVocabulary, vocabulary_config
from pyams_zmi.interfaces import IObjectLabel


__docformat__ = 'restructuredtext'


LOGGER = logging.getLogger('PyAMS (SQLAlchemy)')

CONNECTIONS_TIMESTAMP = {}
CONNECTIONS_LOCK = Lock()


@listens_for(Pool, 'checkout')
def handle_pool_checkout(connection, record, proxy):  # pylint: disable=unused-argument
    """Pool connection checkout

    Called when a connection is retrieved from the pool.
    If the connection record is already marked, we remove it from the mapping.
    """
    with CONNECTIONS_LOCK:
        if record in CONNECTIONS_TIMESTAMP:
            LOGGER.debug("Removing timestamp for checked-out connection "
                         "{0!r} ({1!r})".format(connection, record))
            del CONNECTIONS_TIMESTAMP[record]


@listens_for(Pool, 'checkin')
def handle_pool_checkin(connection, record):
    """Pool connection checkin

    Called when a connection returns to the pool.
    We apply a timestamp on the connection record to be able to close it automatically
    after 5 minutes without being used.
    """
    with CONNECTIONS_LOCK:
        LOGGER.debug("Setting inactivity timestamp for checked-in connection "
                     "{0!r} ({1!r})".format(connection, record))
        CONNECTIONS_TIMESTAMP[record] = datetime.utcnow()


class ConnectionCleanerThread(Thread):
    """Background thread used to clean unused database connections

    Each connection is referenced in CONNECTION_TIMESTAMPS mapping on checkin and is invalidated
    if not being used after given timeout (5 minutes by default)
    """

    def __init__(self, timeout=300, *args, **kwargs):  # pylint: disable=keyword-arg-before-vararg
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def run(self):
        while True:
            now = datetime.utcnow()
            for connection, value in list(CONNECTIONS_TIMESTAMP.items()):
                delta = now - value
                if delta.total_seconds() > self.timeout:
                    LOGGER.debug("Invalidating unused connection {0!r} "
                                 "from pool".format(connection))
                    with CONNECTIONS_LOCK:
                        connection.invalidate()
                        del CONNECTIONS_TIMESTAMP[connection]
            time.sleep(60)


class AlchemyEngineUtility:  # pylint: disable=too-many-instance-attributes
    """SQLAlchemy engine utility"""

    name = FieldProperty(IAlchemyEngineUtility['name'])
    dsn = FieldProperty(IAlchemyEngineUtility['dsn'])
    echo = FieldProperty(IAlchemyEngineUtility['echo'])
    use_pool = FieldProperty(IAlchemyEngineUtility['use_pool'])
    pool_size = FieldProperty(IAlchemyEngineUtility['pool_size'])
    pool_recycle = FieldProperty(IAlchemyEngineUtility['pool_recycle'])
    echo_pool = FieldProperty(IAlchemyEngineUtility['echo_pool'])
    encoding = FieldProperty(IAlchemyEngineUtility['encoding'])
    convert_unicode = FieldProperty(IAlchemyEngineUtility['convert_unicode'])
    twophase = FieldProperty(IAlchemyEngineUtility['twophase'])

    def __init__(self, name='', dsn='', echo=False, use_pool=True, pool_size=25, pool_recycle=-1,
                 echo_pool=False, encoding='utf-8', convert_unicode=False, twophase=True,
                 **kwargs):
        # pylint: disable=too-many-arguments
        self.name = name
        self.dsn = dsn
        self.echo = echo
        self.use_pool = use_pool
        self.pool_size = pool_size
        self.pool_recycle = pool_recycle
        self.echo_pool = echo_pool
        self.encoding = encoding
        self.convert_unicode = convert_unicode
        self.twophase = twophase
        self.kw = PersistentMapping()  # pylint: disable=invalid-name
        self.kw.update(kwargs)

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if (key != '_v_engine') and hasattr(self, '_v_engine'):
            delattr(self, '_v_engine')

    def get_engine(self, use_pool=True):
        """SQLAlchemy engine getter"""
        kw = {}  # pylint: disable=invalid-name
        kw.update(self.kw)
        if not (use_pool and self.use_pool):
            # Always create a new engine when pooling is disabled to help engine disposal
            return create_engine(self.dsn,
                                 echo=self.echo,
                                 poolclass=NullPool,
                                 encoding=self.encoding,
                                 convert_unicode=self.convert_unicode,
                                 **kw)
        # Store engine into volatile attributes when pooling is enabled
        engine = getattr(self, '_v_engine', None)
        if engine is None:
            # pylint: disable=attribute-defined-outside-init
            engine = self._v_engine = \
                create_engine(self.dsn,
                              echo=self.echo,
                              pool_size=self.pool_size,
                              pool_recycle=self.pool_recycle,
                              echo_pool=self.echo_pool,
                              encoding=self.encoding,
                              convert_unicode=self.convert_unicode,
                              **kw)
        return engine

    def clear_engine(self):
        """Clear engine"""
        if hasattr(self, '_v_engine'):
            delattr(self, '_v_engine')


@factory_config(IAlchemyEngineUtility)
class PersistentAlchemyEngineUtility(Persistent, AlchemyEngineUtility, Contained):
    """Persistent implementation of SQLAlchemy engine utility"""


@adapter_config(required=IAlchemyEngineUtility,
                provides=IObjectLabel)
def alchemy_engine_label(context):
    """SQLAlchemy engine table element name factory"""
    return context.name


@adapter_config(required=IAlchemyEngineUtility,
                provides=IViewContextPermissionChecker)
class AlchemyEnginePermissionChecker(ContextAdapter):
    """SQLAlchemy engine permission checker"""

    edit_permission = MANAGE_SQL_ENGINES_PERMISSION


@subscriber(IObjectAddedEvent, context_selector=IAlchemyEngineUtility)
def handle_added_engine(event):
    """Register new SQLAlchemy engine when added"""
    sm = get_parent(event.newParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        sm.getSiteManager().registerUtility(event.object, IAlchemyEngineUtility,
                                            name=event.object.name or '')


@subscriber(IObjectModifiedEvent, context_selector=IAlchemyEngineUtility)
def handle_modified_engine(event):
    """Clear SQLAlchemy engine volatile attributes when modified"""
    IAlchemyEngineUtility(event.object).clear_engine()


@subscriber(IObjectRemovedEvent, context_selector=IAlchemyEngineUtility)
def handle_removed_engine(event):
    """Un-register an SQLAlchemy engine when deleted"""
    sm = get_parent(event.oldParent, ISiteRoot)  # pylint: disable=invalid-name
    if sm is not None:
        sm.getSiteManager().unregisterUtility(event.object, IAlchemyEngineUtility,
                                              name=event.object.name or '')


def get_engine(engine, use_pool=True):
    """Get engine matching given utility name"""
    if isinstance(engine, str):
        engine = query_utility(IAlchemyEngineUtility, name=engine)
        if engine is not None:
            return engine.get_engine(use_pool), engine.twophase
    return None


def get_session(engine, join=True, status=STATUS_ACTIVE, request=None, alias=None,
                twophase=True, use_zope_extension=True, use_pool=True):
    # pylint: disable=too-many-arguments
    """Get a new SQLAlchemy session

    Session is stored in request and in session storage.
    See :func:`get_user_session` function to get arguments documentation.
    """
    if request is None:
        request = check_request()
    if not alias:
        alias = engine
    session_data = get_request_data(request, REQUEST_SESSION_KEY, {})
    session = session_data.get(alias)
    if session is None:
        _engine, _twophase = get_engine(engine, use_pool)
        if use_zope_extension:
            factory = scoped_session(sessionmaker(bind=_engine,
                                                  twophase=twophase and _twophase))
        else:
            factory = sessionmaker(bind=_engine, twophase=twophase and _twophase)
        session = factory()
        if use_zope_extension:
            register(session, initial_state=status)
        if join:
            join_transaction(session, initial_state=status)
        if status != STATUS_READONLY:
            _SESSION_STATE[session] = session
        if session is not None:
            session_data[alias] = session
            set_request_data(request, REQUEST_SESSION_KEY, session_data)
    LOGGER.debug("Using SQLAlchemy session {0!r}".format(session))
    return session


def get_user_session(engine, join=True, status=STATUS_ACTIVE, request=None, alias=None,
                     twophase=True, use_zope_extension=True, use_pool=True):
    # pylint: disable=too-many-arguments
    """Get a new SQLAlchemy session

    :param str engine: name of an SQLAlchemy engine session utility; if *engine* is not given as
        a string, it is returned as-is.
    :param bool join: if *True*, session is joined to the current Pyramid transaction
    :param str status: status of the new session; can be STATUS_ACTIVE or STATUS_READONLY
    :param request: currently running request
    :param str alias: alias to use in connections mapping for this session
    :param bool twophase: if *False*, session will be isolated and not included into two-phase
        transactions mechanism
    :param bool use_zope_extension: if *True*, use ZopeTransactionExtension scoped session
    :param bool use_pool: if *True*, this session will use a pool
    """
    if isinstance(engine, str):
        session = get_session(engine, join, status, request, alias,
                              twophase, use_zope_extension, use_pool)
    else:
        session = engine
    return session


@vocabulary_config(name=ALCHEMY_ENGINES_VOCABULARY)
class EnginesVocabulary(LocalUtilitiesVocabulary):
    """SQLAlchemy engines vocabulary"""

    interface = IAlchemyEngineUtility
