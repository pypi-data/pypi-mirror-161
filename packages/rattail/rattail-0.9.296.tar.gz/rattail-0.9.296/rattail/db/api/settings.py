# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2022 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Settings API
"""

from __future__ import unicode_literals, absolute_import

import warnings

from rattail.db import Session, model


def get_setting(session, name):
    """
    Returns a setting value from the database.
    """
    warnings.warn("function is deprecated, please use "
                  "AppHandler.get_setting() instead",
                  DeprecationWarning)

    local_session = False
    if session is None:
        session = Session()
        local_session = True
    setting = session.query(model.Setting).get(name)
    value = None if setting is None else setting.value
    if local_session:
        session.close()
    return value


def save_setting(session, name, value):
    """
    Saves a setting to the database.
    """
    warnings.warn("function is deprecated, please use "
                  "AppHandler.save_setting() instead",
                  DeprecationWarning)

    local_session = False
    if session is None:
        session = Session()
        local_session = True
    setting = session.query(model.Setting).get(name)
    if not setting:
        setting = model.Setting(name=name)
        session.add(setting)
    setting.value = value
    if local_session:
        session.commit()
        session.close()
