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

"""PyAMS_alchemy.loader module

This module defines a base class which can be used to duplicate entities from one session
to another one.
"""

__docformat__ = 'restructuredtext'

import logging

from sqlalchemy.orm import make_transient

from pyams_alchemy.engine import get_user_session


LOGGER = logging.getLogger('PyAMS (alchemy)')


class DataLoader:
    """SQLAlchemy data loader

    This utility class is used to migrate entities from a given connection
    to another one.
    WARNING: actually, given entities must share the same schema name!!!
    """

    def __init__(self, source, target, entities):
        """
        Initialize data loader

        :param source: name of registered source engine
        :param target: name of registered target engine
        :param entities: list of migrated entities
        """
        self.source_session = get_user_session(source)
        self.target_session = get_user_session(target)
        self.entities = entities

    def run(self):
        """Run data loader"""
        source = self.source_session
        target = self.target_session
        for entity in self.entities:
            LOGGER.info('Loading entity {0!r}'.format(entity))
            for record in source.query(entity):
                source.expunge(record)
                make_transient(record)
                target.add(record)
