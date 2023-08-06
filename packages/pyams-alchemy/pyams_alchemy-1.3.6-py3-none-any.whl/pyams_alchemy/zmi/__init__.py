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

"""PyAMS_alchemy.zmi module

This module defines main SQLAlchemy manager administration components.
"""

from pyramid.view import view_config
from zope.interface import Interface

from pyams_alchemy.interfaces import IAlchemyManager, MANAGE_SQL_ENGINES_PERMISSION
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.url import absolute_url
from pyams_viewlet.manager import viewletmanager_config
from pyams_zmi.helper.container import delete_container_element
from pyams_zmi.interfaces import IAdminLayer, IObjectLabel
from pyams_zmi.interfaces.table import ITableElementEditor
from pyams_zmi.interfaces.viewlet import IMenuHeader, IPropertiesMenu, ISiteManagementMenu
from pyams_zmi.table import NameColumn, Table, TableAdminView, \
    TableElementEditor, TrashColumn
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem


__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


ALCHEMY_MANAGER_LABEL = _("SQL connections")


@adapter_config(required=(IAlchemyManager, IPyAMSLayer, Interface),
                provides=IObjectLabel)
def alchemy_manager_label(context, request, view):
    """Alchemy manager label"""
    return request.localizer.translate(ALCHEMY_MANAGER_LABEL)


@adapter_config(required=(IAlchemyManager, IAdminLayer, Interface, ISiteManagementMenu),
                provides=IMenuHeader)
def alchemy_manager_menu_header(context, request, view, manager):  # pylint: disable=unused-argument
    """SQLAlchemy manager menu header"""
    return ALCHEMY_MANAGER_LABEL


@adapter_config(required=(IAlchemyManager, IAdminLayer, Interface),
                provides=ITableElementEditor)
class AlchemyManagerElementEditor(TableElementEditor):
    """SQLAlchemy manager element editor"""

    view_name = 'admin#engines-list.html'
    modal_target = False

    def __new__(cls, context, request, view):  # pylint: disable=unused-argument
        if not request.has_permission(MANAGE_SQL_ENGINES_PERMISSION, context=context):
            return None
        return TableElementEditor.__new__(cls)


@viewletmanager_config(name='engines-list.menu',
                       context=IAlchemyManager, layer=IAdminLayer,
                       manager=ISiteManagementMenu, weight=10,
                       permission=MANAGE_SQL_ENGINES_PERMISSION,
                       provides=IPropertiesMenu)
class AlchemyManagerEnginesListMenu(NavigationMenuItem):
    """SQLAlchemy manager engines list menu"""

    label = _("SQL engines")
    icon_class = 'fas fa-table'
    href = '#engines-list.html'


class AlchemyManagerEnginesTable(Table):
    """SQLAlchemy manager engines table"""

    display_if_empty = True


@adapter_config(required=(IAlchemyManager, IAdminLayer, AlchemyManagerEnginesTable),
                provides=IValues)
class AlchemyManagerEnginesTableValues(ContextRequestViewAdapter):
    """SQLAlchemy manager table values adapter"""

    @property
    def values(self):
        """SQLAlchemy manager table values getter"""
        yield from self.context.values()


@adapter_config(name='name',
                required=(IAlchemyManager, IAdminLayer, AlchemyManagerEnginesTable),
                provides=IColumn)
class AlchemyManagerEnginesNameColumn(NameColumn):
    """SQLAlchemy manager name column"""


@adapter_config(name='trash',
                required=(IAlchemyManager, IAdminLayer, AlchemyManagerEnginesTable),
                provides=IColumn)
class AlchemyManagerEnginesTrashColumn(TrashColumn):
    """SQLAlchemy manager trash column"""

    permission = MANAGE_SQL_ENGINES_PERMISSION


@pagelet_config(name='engines-list.html',
                context=IAlchemyManager, layer=IPyAMSLayer,
                permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyManagerEnginesView(TableAdminView):
    """SQLAlchemy manager engines view"""

    title = _("SQL engines")
    table_class = AlchemyManagerEnginesTable
    table_label = _("List of SQL engines")

    @property
    def back_url(self):
        """Form back URL getter"""
        return absolute_url(self.request.root, self.request, 'admin#utilities.html')  # pylint: disable=no-member

    back_url_target = None


@view_config(name='delete-element.json',
             context=IAlchemyManager, request_type=IPyAMSLayer,
             permission=MANAGE_SQL_ENGINES_PERMISSION, renderer='json', xhr=True)
def delete_sql_engine(request):
    """Delete SQL engine"""
    return delete_container_element(request)
