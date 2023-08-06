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

"""PyAMS_alchemy.zmi.engine module

This module defines SQL engines management components.
"""

from pyramid.events import subscriber
from zope.copy import copy
from zope.interface import Interface, Invalid, implementer

from pyams_alchemy.interfaces import IAlchemyEngineUtility, IAlchemyManager, \
    MANAGE_SQL_ENGINES_PERMISSION
from pyams_alchemy.zmi import AlchemyManagerEnginesTable
from pyams_form.ajax import ajax_form_config
from pyams_form.field import Fields
from pyams_form.interfaces import DISPLAY_MODE
from pyams_form.interfaces.form import IAJAXFormRenderer, IAddForm, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.viewlet.actions import ContextAddAction
from pyams_table.interfaces import IColumn
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.intids import IUniqueID
from pyams_utils.registry import query_utility
from pyams_utils.traversing import get_parent
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.helper.event import get_json_table_row_add_callback, \
    get_json_table_row_refresh_callback
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IToolbarViewletManager
from pyams_zmi.table import ActionColumn, TableElementEditor
from pyams_zmi.utils import get_object_label


__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


class IAlchemyEngineAddForm(IAddForm):
    """SQLAlchemy engine add form interface"""


@subscriber(IDataExtractedEvent, form_selector=IAlchemyEngineAddForm)
def handle_new_engine_data_extraction(event):
    """Handle new engine data"""
    name = event.data['name'] or ''
    engine = query_utility(IAlchemyEngineUtility, name=name)
    if engine is not None:
        event.form.widgets.errors += (Invalid(_("An SQLAlchemy engine is already "
                                                "registered with this name!")),)


@adapter_config(required=(IAlchemyManager, IAdminLayer, IAlchemyEngineAddForm),
                provides=IAJAXFormRenderer)
class AlchemyEngineAddFormRenderer(ContextRequestViewAdapter):
    """Alchemy engine add form AJAX renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        manager = get_parent(self.context, IAlchemyManager)
        return {
            'callbacks': [
                get_json_table_row_add_callback(manager, self.request,
                                                AlchemyManagerEnginesTable, changes)
            ]
        }


#
# Alchemy engine add form
#

@viewlet_config(name='add-sql-engine.menu',
                context=IAlchemyManager, layer=IAdminLayer, view=AlchemyManagerEnginesTable,
                manager=IToolbarViewletManager, weight=10,
                permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyEngineAddAction(ContextAddAction):
    """Alchemy engine add action"""

    label = _("Add SQL engine")
    href = 'add-sql-engine.html'


@implementer(IAlchemyEngineAddForm)
class AlchemyEngineBaseAddFormMixin:
    """Alchemy engine base add form mixin"""

    @property
    def title(self):
        translate = self.request.localizer.translate
        return '<small>{}</small><br />{}'.format(
            get_object_label(self.context, self.request, self),
            translate(_("New SQL engine")))


@ajax_form_config(name='add-sql-engine.html',
                  context=IAlchemyManager, layer=IPyAMSLayer,
                  permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyEngineAddForm(AlchemyEngineBaseAddFormMixin, AdminModalAddForm):  # pylint: disable=abstract-method
    """SQLAlchemy engine add form"""

    legend = _("New engine properties")

    fields = Fields(IAlchemyEngineUtility)
    content_factory = IAlchemyEngineUtility

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context[oid] = obj


#
# Alchemy engine clone form
#

@adapter_config(name='clone',
                required=(IAlchemyManager, IAdminLayer, AlchemyManagerEnginesTable),
                provides=IColumn)
class AlchemyEngineCloneColumn(ActionColumn):
    """SQLAlchemy engine clone column"""

    hint = _("Clone SQL engine")
    icon_class = 'far fa-clone'

    href = 'clone-sql-engine.html'

    weight = 100


@ajax_form_config(name='clone-sql-engine.html',
                  context=IAlchemyEngineUtility, layer=IPyAMSLayer,
                  permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyEngineCloneForm(AlchemyEngineBaseAddFormMixin, AdminModalAddForm):
    """SQLAlchemy engine clone form"""

    legend = _("Clone SQL connection")

    fields = Fields(IAlchemyEngineUtility).select('name')

    def create(self, data):
        return copy(self.context)

    def add(self, obj):
        oid = IUniqueID(obj).oid
        self.context.__parent__[oid] = obj


#
# Alchemy engine edit form
#

@adapter_config(required=(IAlchemyEngineUtility, IAdminLayer, Interface),
                provides=ITableElementEditor)
class AlchemyEngineElementEditor(TableElementEditor):
    """SQLAlchemy engines table element editor"""


@ajax_form_config(name='properties.html',
                  context=IAlchemyEngineUtility, layer=IPyAMSLayer,
                  permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyEngineEditForm(AdminModalEditForm):
    """SQLAlchemy engine properties edit form"""

    @property
    def title(self):
        translate = self.request.localizer.translate
        manager = query_utility(IAlchemyManager)
        return '<small>{}</small><br />{}'.format(
            get_object_label(manager, self.request, self),
            translate(_("SQL engine: {}")).format(self.context.name))

    legend = _("SQL engine properties")

    fields = Fields(IAlchemyEngineUtility)

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        name = self.widgets.get('name')
        if name is not None:
            name.mode = DISPLAY_MODE


@adapter_config(required=(IAlchemyEngineUtility, IAdminLayer, AlchemyEngineEditForm),
                provides=IAJAXFormRenderer)
class AlchemyEngineEditFormAJAXRenderer(ContextRequestViewAdapter):
    """SQLAlchemy engine edit form AJAX renderer"""

    def render(self, changes):
        """AJAX result renderer"""
        if not changes:
            return None
        manager = get_parent(self.context, IAlchemyManager)
        return {
            'callbacks': [
                get_json_table_row_refresh_callback(manager, self.request,
                                                    AlchemyManagerEnginesTable, self.context)
            ]
        }
