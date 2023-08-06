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
Poser Views for Views...
"""

from __future__ import unicode_literals, absolute_import

from rattail.util import simple_error

from webhelpers2.html import HTML, tags

from tailbone.views import MasterView


class PoserMasterView(MasterView):
    """
    Master view base class for Poser
    """
    model_key = 'key'
    filterable = False
    pageable = False

    def __init__(self, request):
        super(PoserMasterView, self).__init__(request)
        app = self.get_rattail_app()
        self.poser_handler = app.get_poser_handler()

        # nb. pre-load all data b/c all views potentially need access
        self.data = self.get_data()

    def get_data(self, session=None):
        if hasattr(self, 'data'):
            return self.data

        try:
            return self.get_poser_data(session)

        except Exception as error:
            self.request.session.flash(simple_error(error), 'error')

            if not self.request.is_root:
                self.request.session.flash("You must become root in order "
                                           "to do Poser Setup.", 'error')
            else:
                link = tags.link_to("Poser Setup",
                                    self.request.route_url('poser_setup'))
                msg = HTML.literal("Please see the {} page.".format(link))
                self.request.session.flash(msg, 'error')
            return []

    def get_poser_data(self, session=None):
        raise NotImplementedError("TODO: you must implement this in subclass")
