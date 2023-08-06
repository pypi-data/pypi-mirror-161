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

"""PyAMS_alchemy.task.interfaces module

This module defines common interfaces of SQLAlchemy scheduler task.
"""

__docformat__ = 'restructuredtext'

from zope.interface import Interface
from zope.schema import Choice, Text

from pyams_alchemy import _
from pyams_alchemy.interfaces import ALCHEMY_CONVERTERS_VOCABULARY, ALCHEMY_ENGINES_VOCABULARY
from pyams_scheduler.interfaces import ITask


class IAlchemyTaskInfo(Interface):
    """SQLAlchemy scheduler task interface"""

    session_name = Choice(title=_("SQL session name"),
                          description=_("Name of the SQLAlchemy engine used to access database"),
                          vocabulary=ALCHEMY_ENGINES_VOCABULARY,
                          required=True)

    query = Text(title=_("SQL query text"),
                 required=True)

    output_format = Choice(title=_("Output format"),
                           description=_("Format into which query output should be returned"),
                           vocabulary=ALCHEMY_CONVERTERS_VOCABULARY,
                           required=True,
                           default='json')


class IAlchemyTask(ITask, IAlchemyTaskInfo):
    """SQLAlchemy task interface"""
