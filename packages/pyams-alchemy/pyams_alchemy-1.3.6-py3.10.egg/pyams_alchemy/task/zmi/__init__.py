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

"""PyAMS_alchemy.task.zmi module

This module provides management components for SQLAlchemy tasks.
"""

from zope.interface import alsoProvides, implementer

from pyams_alchemy.task import AlchemyTask, IAlchemyTask
from pyams_alchemy.task.interfaces import IAlchemyTaskInfo
from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.group import GroupManager
from pyams_form.interfaces.form import IForm, IInnerTabForm
from pyams_form.subform import InnerAddForm, InnerEditForm
from pyams_layer.interfaces import IPyAMSLayer
from pyams_scheduler.interfaces import IScheduler, MANAGE_TASKS_PERMISSION
from pyams_scheduler.zmi import SchedulerTasksTable
from pyams_scheduler.task.zmi import BaseTaskAddForm, BaseTaskEditForm
from pyams_skin.viewlet.menu import MenuItem
from pyams_utils.adapter import adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContextAddingsViewletManager


__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


class IAlchemyTaskForm(IForm):
    """SQLAlchemy task form marker interface"""


@implementer(IAlchemyTaskForm)
class AlchemyTaskFormInfo(GroupManager):
    """SQLAlchemy task form info"""

    title = _("SQL task settings")
    fields = Fields(IAlchemyTaskInfo)

    def update_widgets(self, prefix=None):
        """Widgets update"""
        super().update_widgets(prefix)  # pylint: disable=no-member
        session = self.widgets.get('session_name')  # pylint: disable=no-member
        if session is not None:
            translate = self.request.localizer.translate  # pylint: disable=no-member
            session.placeholder = translate(_("Select connection name..."))
        query = self.widgets.get('query')  # pylint: disable=no-member
        if query is not None:
            query.add_class('height-100')
            query.widget_css_class = "editor height-400px"
            query.object_data = {
                'ams-filename': 'query.sql'
            }
            alsoProvides(query, IObjectData)


@viewlet_config(name='add-sql-task.menu',
                context=IScheduler, layer=IAdminLayer, view=SchedulerTasksTable,
                manager=IContextAddingsViewletManager, weight=100,
                permission=MANAGE_TASKS_PERMISSION)
class AlchemyTaskAddMenu(MenuItem):
    """SQLAlchemy task add menu"""

    label = _("Add SQL query...")
    href = 'add-sql-task.html'
    modal_target = True


@ajax_form_config(name='add-sql-task.html', context=IScheduler, layer=IPyAMSLayer,
                  permission=MANAGE_TASKS_PERMISSION)
class AlchemyTaskAddForm(BaseTaskAddForm):
    """SQLAlchemy task add form"""

    modal_class = 'modal-xl'

    content_factory = IAlchemyTask
    content_label = AlchemyTask.label


@adapter_config(name='sql-task-info.form',
                required=(IScheduler, IAdminLayer, AlchemyTaskAddForm),
                provides=IInnerTabForm)
class AlchemyTaskAddFormInfo(AlchemyTaskFormInfo, InnerAddForm):
    """SQLAlchemy task add form info"""


@ajax_form_config(name='properties.html', context=IAlchemyTask, layer=IPyAMSLayer,
                  permission=MANAGE_TASKS_PERMISSION)
class AlchemyTaskEditForm(BaseTaskEditForm):
    """SQLAlchemy task edit form"""

    modal_class = 'modal-xl'


@adapter_config(name='sql-task-info.form',
                required=(IAlchemyTask, IAdminLayer, AlchemyTaskEditForm),
                provides=IInnerTabForm)
class AlchemyTaskEditFormInfo(AlchemyTaskFormInfo, InnerEditForm):
    """SQLAlchemy task edit form info"""
