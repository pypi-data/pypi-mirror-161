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

"""PyAMS_alchemy.task module

This module defines a PyAMS_scheduler task which can be used to schedule
any SQL command execution.
"""

import sys
import traceback

from sqlalchemy.exc import ResourceClosedError, SQLAlchemyError
from zope.schema.fieldproperty import FieldProperty

from pyams_alchemy.engine import get_user_session
from pyams_alchemy.interfaces import IAlchemyConverter
from pyams_alchemy.task.interfaces import IAlchemyTask
from pyams_scheduler.interfaces.task import TASK_STATUS_EMPTY, TASK_STATUS_ERROR, \
    TASK_STATUS_FAIL, TASK_STATUS_OK
from pyams_scheduler.task import Task
from pyams_utils.factory import factory_config
from pyams_utils.registry import get_utility


__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


@factory_config(IAlchemyTask)
class AlchemyTask(Task):
    """SQLAlchemy task"""

    label = _("SQL query")
    icon_class = 'fas fa-database'

    session_name = FieldProperty(IAlchemyTask['session_name'])
    query = FieldProperty(IAlchemyTask['query'])
    output_format = FieldProperty(IAlchemyTask['output_format'])

    def run(self, report, **kwargs):  # pylint: disable=unused-argument
        """Run SQL query task"""
        try:
            session = get_user_session(self.session_name,
                                       join=False,
                                       twophase=False,
                                       use_zope_extension=False)
            try:
                report.write('SQL query output\n'
                             '================\n')
                report.write('SQL query: \n    {}\n\n'.format(
                    self.query.replace('\r', '').replace('\n', '\n    ')))
                results = session.execute(self.query)
                session.commit()
                converter = get_utility(IAlchemyConverter, name=self.output_format)
                result = converter.convert(results)
                report.write(f'SQL output ({results.rowcount} records):\n\n')
                report.write(result)
                return TASK_STATUS_OK, result
            except ResourceClosedError:
                report.write('SQL query returned no result.\n')
                return TASK_STATUS_EMPTY, None
        except SQLAlchemyError:
            session.rollback()
            etype, value, tb = sys.exc_info()  # pylint: disable=invalid-name
            report.write('\n\n'
                         'An SQL error occurred\n'
                         '=====================\n')
            report.write(''.join(traceback.format_exception(etype, value, tb)))
            return TASK_STATUS_FAIL, None
