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

"""PyAMS_alchemy.zmi.test module

This module defines SQLAlchemy engines test components.
"""

from html import escape
from itertools import tee

from sqlalchemy.exc import DatabaseError, ResourceClosedError
from zope.interface import Interface, alsoProvides
from zope.schema import Text

from pyams_alchemy.engine import get_user_session
from pyams_alchemy.interfaces import IAlchemyEngineUtility, IAlchemyManager, \
    MANAGE_SQL_ENGINES_PERMISSION
from pyams_alchemy.zmi import AlchemyManagerEnginesTable
from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IGroup
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.viewlet import IFormFooterViewletManager
from pyams_skin.schema.button import CloseButton, SubmitButton
from pyams_skin.viewlet.help import AlertMessage
from pyams_table.column import GetAttrColumn
from pyams_table.interfaces import IColumn, IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.interfaces.data import IObjectData
from pyams_utils.list import boolean_iter
from pyams_viewlet.viewlet import EmptyViewlet, ViewContentProvider, viewlet_config
from pyams_zmi.form import AdminModalAddForm, FormGroupSwitcher
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.table import ButtonColumn, InnerTableAdminView, Table


__docformat__ = 'restructuredtext'

from pyams_alchemy import _  # pylint: disable=ungrouped-imports


@adapter_config(name='test',
                required=(IAlchemyManager, IAdminLayer, AlchemyManagerEnginesTable),
                provides=IColumn)
class AlchemyManagerTestColumn(ButtonColumn):
    """SQLAlchemy manager name column"""

    label = _("Test engine")
    status = 'secondary'

    permission = MANAGE_SQL_ENGINES_PERMISSION
    href = 'test-sql-engine.html'
    modal_target = True

    weight = 50


class IAlchemyEngineTestQuery(Interface):
    """SQLAlchemy engine test interface"""

    query = Text(title=_("SQL query"),
                 description=_("Enter valid SQL code; WARNING: query will NOT be committed!!"),
                 required=True)


class IAlchemyEngineTestButtons(Interface):
    """SQLAlchemy engine test buttons"""

    test = SubmitButton(name='test',
                        title=_("Execute query"))

    close = CloseButton(name='close',
                        title=_("Close"))


@ajax_form_config(name='test-sql-engine.html',
                  context=IAlchemyEngineUtility, layer=IPyAMSLayer,
                  permission=MANAGE_SQL_ENGINES_PERMISSION)
class AlchemyEngineTestForm(AdminModalAddForm):
    # pylint: disable=abstract-method
    """SQLAlchemy engine test form"""

    @property
    def title(self):
        """Form title getter"""
        return self.request.localizer.translate(_("SQL engine: {}")).format(self.context.name)

    modal_class = 'modal-max'

    fields = Fields(Interface)
    buttons = Buttons(IAlchemyEngineTestButtons)

    @handler(IAlchemyEngineTestButtons['test'])
    def handle_test(self, action):
        """Query test button handler"""
        data, errors = self.extract_data()
        if not errors:
            self.finished_state.update({
                'action': action,
                'changes': data
            })


@adapter_config(name='query',
                required=(IAlchemyEngineUtility, IAdminLayer, AlchemyEngineTestForm),
                provides=IGroup)
class AlchemyEngineQueryGroup(FormGroupSwitcher):
    """SQLAlchemy engine query group"""

    legend = _("Test SQLAlchemy engine")
    fields = Fields(IAlchemyEngineTestQuery)
    switcher_mode = 'always'

    def update_widgets(self, prefix=None):
        super().update_widgets(prefix)
        query = self.widgets.get('query')
        if query is not None:
            query.add_class('height-100')
            query.widget_css_class = "editor height-100px"
            query.object_data = {
                'ams-filename': 'query.sql'
            }
            alsoProvides(query, IObjectData)


@adapter_config(name='test',
                required=(IAlchemyEngineUtility, IAdminLayer, AlchemyEngineTestForm),
                provides=IAJAXFormRenderer)
class AlchemyEngineTestActionRenderer(ContextRequestViewAdapter):
    """SQLAlchemy engine test action renderer"""

    def render(self, changes):
        """AJAX form renderer"""
        if not changes:
            return None
        test_view = AlchemyEngineTestView(self.context, self.request, self.view)
        try:
            test_view.update()
        except DatabaseError as exc:
            return {
                'status': 'error',
                'messages': [
                    escape('{!r}'.format(exc))
                ]
            }
        return {
            'status': 'success',
            'content': {
                'target': '#{}-test-target'.format(self.view.id),
                'html': test_view.render()
            },
            'closeForm': False
        }


@viewlet_config(name='engine-test.target',
                context=IAlchemyEngineUtility, layer=IAdminLayer, view=AlchemyEngineTestForm,
                manager=IFormFooterViewletManager, weight=20)
class AlchemyEngineTestTarget(EmptyViewlet):
    """SQLAlchemy engine test target"""

    def render(self):
        """Viewlet renderer"""
        return '<div id="{}-test-target" class="hidden"></div>'.format(self.view.id)


class SQLColumn(GetAttrColumn):
    """SQL column"""

    default_value = '--'

    def __init__(self, context, request, table, col):
        super().__init__(context, request, table)
        self.__name__ = col
        self.header = col
        self.attr_name = col

    def get_value(self, obj):
        if obj is not None and self.attr_name is not None:
            value = getattr(obj, self.attr_name)
            if value is None:
                value = escape('<NULL>')
            return value
        return self.default_value


class AlchemyEngineTestTable(Table):
    """SQLAlchemy engine test table"""

    batch_size = 999
    sort_on = None

    results = ()

    css_classes = {
        'table': 'table table-striped table-hover table-xs datatable'
    }

    @property
    def object_data(self):
        """Table data getter"""
        result = super().object_data.copy()
        result.update({
            'col-reorder': True,
            'buttons': 'all',
            'order': []
        })
        return result

    def update(self):
        data = self.form.finished_state.get('changes')  # pylint: disable=no-member
        if 'query' in data:
            session = get_user_session(self.context.name, join=False, twophase=False,
                                       use_zope_extension=False)
            try:
                self.results = list(session.execute(data['query']))
            except ResourceClosedError:
                pass
        super().update()

    def init_columns(self):
        columns = []
        has_values, values = boolean_iter(self.values)
        if has_values:
            rows, _values = tee(values)
            try:
                row = next(rows)
            except StopIteration:
                pass
            else:
                for col in row.keys():
                    column = SQLColumn(self.context, self.request, self, col)
                    columns.append(column)
        self.columns = columns

    def render(self):
        result = super().render()
        if len(self.rows) == self.batch_size:
            alert = AlertMessage(self.context, self.request, self, None)
            alert.status = 'warning'
            alert.css_class = 'p-1 mb-0'
            # pylint: disable=protected-access
            alert._message = self.request.localizer.translate(
                _("Request results contains more than {batch} records; only the "
                  "first records are displayed.")).format(batch=self.batch_size)
            alert.update()
            result += alert.render()
        return result


@adapter_config(required=(IAlchemyEngineUtility, IAdminLayer, AlchemyEngineTestTable),
                provides=IValues)
class AlchemyEngineTestTableValues(ContextRequestViewAdapter):
    """SQLAlchemy engine test table values"""

    @property
    def values(self):
        """Alchemy engine test table values getter"""
        yield from self.view.results


class AlchemyEngineTestView(InnerTableAdminView, ViewContentProvider):
    """SQLAlchemy engine test view"""

    title = _("SQLAlchemy engine test")
    table_class = AlchemyEngineTestTable
    table_label = _("SQL query results")

    def __init__(self, context, request, form):
        super().__init__(context, request)
        self.table.form = form
