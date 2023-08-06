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

"""PyAMS_alchemy.converter.json module

This module provides an utility which can be used to convert an SQLAlchemy
results proxy to JSON.
"""

__docformat__ = 'restructuredtext'

import json

from pyams_alchemy.interfaces import IAlchemyConverter
from pyams_utils.registry import utility_config


@utility_config(name='json',
                provides=IAlchemyConverter)
class JSONAlchemyConverter:
    """SQLAlchemy converter to JSON format"""

    @staticmethod
    def convert(rows, **kwargs):  # pylint: disable=unused-argument
        """Convert provided rows to JSON"""
        result = []
        append = result.append
        keys = rows.keys()
        for row in rows:
            value = dict(((key, row[key]) for key in keys))
            append(value)
        return json.dumps(result)
