#
# Copyright (c) 2015-2019 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_alchemy.interfaces module

This module defines mail package interfaces.
"""

from zope.annotation import IAttributeAnnotatable
from zope.container.constraints import contains
from zope.container.interfaces import IContainer
from zope.interface import Interface
from zope.schema import Bool, Choice, Int, TextLine

from pyams_security.interfaces import IContentRoles
from pyams_security.schema import PrincipalsSetField
from pyams_utils.interfaces import ENCODINGS_VOCABULARY_NAME

from pyams_alchemy import _


#
# SQLAlchemy manager permissions
#

MANAGE_SQL_ENGINES_PERMISSION = 'pyams.ManageAlchemyEngines'
'''Permission used to manage SQLAlchemy engines'''

SQL_MANAGER_ROLE = 'pyams.AlchemyManager'
'''SQL engines manager role'''


#
# SQLAlchemy engine interfaces
#

REQUEST_SESSION_KEY = 'pyams_alchemy.session'

ALCHEMY_ENGINES_VOCABULARY = 'pyams_alchemy.engines'


class IAlchemyEngineUtility(IAttributeAnnotatable):
    """SQLAlchemy engine definition interface"""

    name = TextLine(title=_("Engine name"),
                    description=_("Keep empty if this engine is the default engine..."),
                    required=False,
                    default='')

    dsn = TextLine(title=_('DSN'),
                   description=_('RFC-1738 compliant URL for the database connection'),
                   required=True,
                   default=u'sqlite://')

    echo = Bool(title=_('Echo SQL?'),
                description=_("Log all SQL statements to system logger"),
                required=True,
                default=False)

    use_pool = Bool(title=_("Use connections pool?"),
                    description=_("If 'no', collections pooling will be disabled"),
                    required=True,
                    default=True)

    pool_size = Int(title=_("Pool size"),
                    description=_("SQLAlchemy connections pool size"),
                    required=False,
                    default=25)

    pool_recycle = Int(title=_("Pool recycle time"),
                       description=_("SQLAlchemy connection recycle time (-1 for none)"),
                       required=False,
                       default=-1)

    echo_pool = Bool(title=_("Echo pool?"),
                     description=_("Log all pool checkouts/checkins to system logger?"),
                     required=True,
                     default=False)

    encoding = Choice(title=_('Encoding'),
                      required=True,
                      vocabulary=ENCODINGS_VOCABULARY_NAME,
                      default='utf-8')

    convert_unicode = Bool(title=_('Convert Unicode'),
                           required=True,
                           default=False)

    twophase = Bool(title=_("Two-phases commit?"),
                    description=_("Disable this option if two-phases commits should be "
                                  "disabled (for SQLite for example)"),
                    required=True,
                    default=True)

    def get_engine(self, use_pool=True):
        """Get SQLAlchemy engine"""

    def clear_engine(self):
        """Remove inner volatile attributes when utility properties are modified"""


ALCHEMY_MANAGER_NAME = 'SQL connections'


class IAlchemyManager(IContainer):
    """SQLAlchemy engines container"""

    contains(IAlchemyEngineUtility)


class IAlchemyManagerRoles(IContentRoles):
    """SQLAlchemy manager roles"""

    sql_managers = PrincipalsSetField(title=_("SQL managers"),
                                      role_id=SQL_MANAGER_ROLE,
                                      required=False)


ALCHEMY_CONVERTERS_VOCABULARY = 'pyams_alchemy.converters'


class IAlchemyConverter(Interface):
    """Utility interface provided to convert an SQLAlchemy result proxy"""

    def convert(self, rows, **kwargs):
        """Convert provided rows to format provided by converter"""
