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

"""PyAMS_alchemy.manager module

This module defines an SQLAlchemy "manager", which is just a
container for SQLAlchemy engines definitions.
"""

from zope.container.folder import Folder
from zope.interface import implementer

from pyams_alchemy.interfaces import IAlchemyManager, IAlchemyManagerRoles
from pyams_security.interfaces import IDefaultProtectionPolicy, IRolesPolicy
from pyams_security.property import RolePrincipalsFieldProperty
from pyams_security.security import ProtectedObjectMixin, ProtectedObjectRoles
from pyams_utils.adapter import ContextAdapter, adapter_config
from pyams_utils.factory import factory_config


__docformat__ = 'restructuredtext'


@factory_config(IAlchemyManager)
@implementer(IDefaultProtectionPolicy)
class AlchemyManager(ProtectedObjectMixin, Folder):
    """SQLAlchemy engines container"""


@implementer(IAlchemyManagerRoles)
class AlchemyManagerRoles(ProtectedObjectRoles):
    """SQLAlchemy manager roles"""

    sql_managers = RolePrincipalsFieldProperty(IAlchemyManagerRoles['sql_managers'])


@adapter_config(required=IAlchemyManager,
                provides=IAlchemyManagerRoles)
def alchemy_manager_roles_adapter(context):
    """SQLAlchemy manager roles adapter"""
    return AlchemyManagerRoles(context)


@adapter_config(name='alchemy_roles',
                required=IAlchemyManager,
                provides=IRolesPolicy)
class AlchemyManagerRolesPolicy(ContextAdapter):
    """SQLAlchemy manager roles policy"""

    roles_interface = IAlchemyManagerRoles
    weight = 20
