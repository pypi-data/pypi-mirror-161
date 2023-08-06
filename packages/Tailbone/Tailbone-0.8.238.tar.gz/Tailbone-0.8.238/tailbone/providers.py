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
Providers for Tailbone features
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import load_entry_points


class TailboneProvider(object):
    """
    Base class for Tailbone providers.  These are responsible for
    declaring which things a given project makes available to the app.
    (Or at least the things which should be easily configurable.)
    """

    def __init__(self, config):
        self.config = config

    def configure_db_sessions(self, rattail_config, pyramid_config):
        pass

    def get_static_includes(self):
        pass

    def get_provided_views(self):
        return {}


def get_all_providers(config):
    """
    Returns a dict of all registered providers.
    """
    providers = load_entry_points('tailbone.providers')
    for key in list(providers):
        providers[key] = providers[key](config)
    return providers
