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

import six

import colander

from .master import PoserMasterView
from tailbone.providers import get_all_providers


class PoserViewView(PoserMasterView):
    """
    Master view for Poser views
    """
    normalized_model_name = 'poser_view'
    model_title = "Poser View"
    route_prefix = 'poser_views'
    url_prefix = '/poser/views'
    configurable = True
    config_title = "Included Views"

    # TODO
    creatable = False
    editable = False
    deletable = False
    # downloadable = True

    grid_columns = [
        'key',
        'class_name',
        'description',
        'error',
    ]

    def get_poser_data(self, session=None):
        return self.poser_handler.get_all_tailbone_views()

    def make_form_schema(self):
        return PoserViewSchema()

    def make_create_form(self):
        return self.make_form({})

    def configure_form(self, f):
        super(PoserViewView, self).configure_form(f)
        view = f.model_instance

        # key
        f.set_default('key', 'cool_widget')
        f.set_helptext('key', "Unique key for the view; used as basis for filename.")
        if self.creating:
            f.set_validator('view_key', self.unique_view_key)

        # class_name
        f.set_default('class_name', "CoolWidget")
        f.set_helptext('class_name', "Python-friendly basis for view class name.")

        # description
        f.set_default('description', "Master view for Cool Widgets")
        f.set_helptext('description', "Brief description of the view.")

    def unique_view_key(self, node, value):
        for view in self.get_data():
            if view['key'] == value:
                raise node.raise_invalid("Poser view key must be unique")

    def collect_available_view_settings(self):

        # TODO: this probably should be more dynamic?  definitely need
        # to let integration packages register some more options...

        everything = {'rattail': {

            'people': {

                # TODO: need some way for integration / extension
                # packages to register alternate view options for some
                # of these.  that is the main reason these are dicts
                # even though at the moment it's a bit overkill.

                'tailbone.views.customers': {
                    # 'spec': 'tailbone.views.customers',
                    'label': "Customers",
                },
                'tailbone.views.customergroups': {
                    # 'spec': 'tailbone.views.customergroups',
                    'label': "Customer Groups",
                },
                'tailbone.views.employees': {
                    # 'spec': 'tailbone.views.employees',
                    'label': "Employees",
                },
                'tailbone.views.members': {
                    # 'spec': 'tailbone.views.members',
                    'label': "Members",
                },
            },

            'products': {

                'tailbone.views.departments': {
                    # 'spec': 'tailbone.views.departments',
                    'label': "Departments",
                },

                'tailbone.views.ifps': {
                    # 'spec': 'tailbone.views.ifps',
                    'label': "IFPS PLU Codes",
                },

                'tailbone.views.subdepartments': {
                    # 'spec': 'tailbone.views.subdepartments',
                    'label': "Subdepartments",
                },

                'tailbone.views.vendors': {
                    # 'spec': 'tailbone.views.vendors',
                    'label': "Vendors",
                },

                'tailbone.views.products': {
                    # 'spec': 'tailbone.views.products',
                    'label': "Products",
                },

                'tailbone.views.brands': {
                    # 'spec': 'tailbone.views.brands',
                    'label': "Brands",
                },

                'tailbone.views.categories': {
                    # 'spec': 'tailbone.views.categories',
                    'label': "Categories",
                },

                'tailbone.views.depositlinks': {
                    # 'spec': 'tailbone.views.depositlinks',
                    'label': "Deposit Links",
                },

                'tailbone.views.families': {
                    # 'spec': 'tailbone.views.families',
                    'label': "Families",
                },

                'tailbone.views.reportcodes': {
                    # 'spec': 'tailbone.views.reportcodes',
                    'label': "Report Codes",
                },
            },

            'batches': {

                'tailbone.views.batch.delproduct': {
                    'label': "Delete Product",
                },
                'tailbone.views.batch.inventory': {
                    'label': "Inventory",
                },
                'tailbone.views.batch.labels': {
                    'label': "Labels",
                },
                'tailbone.views.batch.newproduct': {
                    'label': "New Product",
                },
                'tailbone.views.batch.pricing': {
                    'label': "Pricing",
                },
                'tailbone.views.batch.product': {
                    'label': "Product",
                },
                'tailbone.views.batch.vendorcatalog': {
                    'label': "Vendor Catalog",
                },
            },

            'other': {

                'tailbone.views.datasync': {
                    # 'spec': 'tailbone.views.datasync',
                    'label': "DataSync",
                },

                'tailbone.views.importing': {
                    # 'spec': 'tailbone.views.importing',
                    'label': "Importing / Exporting",
                },

                'tailbone.views.stores': {
                    # 'spec': 'tailbone.views.stores',
                    'label': "Stores",
                },

                'tailbone.views.taxes': {
                    # 'spec': 'tailbone.views.taxes',
                    'label': "Taxes",
                },
            },
        }}

        for key, views in six.iteritems(everything['rattail']):
            for vkey, view in six.iteritems(views):
                view['options'] = [vkey]

        providers = get_all_providers(self.rattail_config)
        for provider in six.itervalues(providers):

            # loop thru provider top-level groups
            for topkey, groups in six.iteritems(provider.get_provided_views()):

                # get or create top group
                topgroup = everything.setdefault(topkey, {})

                # loop thru provider view groups
                for key, views in six.iteritems(groups):

                    # add group to top group, if it's new
                    if key not in topgroup:
                        topgroup[key] = views

                        # also must init the options for group
                        for vkey, view in six.iteritems(views):
                            view['options'] = [vkey]

                    else: # otherwise must "update" existing group

                        # get ref to existing ("standard") group
                        stdgroup = topgroup[key]

                        # loop thru views within provider group
                        for vkey, view in six.iteritems(views):

                            # add view to group if it's new
                            if vkey not in stdgroup:
                                view['options'] = [vkey]
                                stdgroup[vkey] = view

                            else: # otherwise "update" existing view
                                stdgroup[vkey]['options'].append(view['spec'])

        return everything

    def configure_get_simple_settings(self):
        settings = []

        view_settings = self.collect_available_view_settings()
        for topgroup in six.itervalues(view_settings):
            for view_section, section_settings in six.iteritems(topgroup):
                for key in section_settings:
                    settings.append({'section': 'tailbone.includes',
                                     'option': key})

        return settings

    def configure_get_context(self, simple_settings=None,
                              input_file_templates=True):

        # first get normal context
        context = super(PoserViewView, self).configure_get_context(
            simple_settings=simple_settings,
            input_file_templates=input_file_templates)

        # first add available options
        view_settings = self.collect_available_view_settings()
        view_options = {}
        for topgroup in six.itervalues(view_settings):
            for key, views in six.iteritems(topgroup):
                for vkey, view in six.iteritems(views):
                    view_options[vkey] = view['options']
        context['view_options'] = view_options

        # then add all available settings as sorted (key, label) options
        for topkey, topgroup in six.iteritems(view_settings):
            for key in list(topgroup):
                settings = topgroup[key]
                settings = [(key, setting.get('label', key))
                            for key, setting in six.iteritems(settings)]
                settings.sort(key=lambda itm: itm[1])
                topgroup[key] = settings
        context['view_settings'] = view_settings

        return context

    def configure_flash_settings_saved(self):
        super(PoserViewView, self).configure_flash_settings_saved()
        self.request.session.flash("Please restart the web app!", 'warning')


class PoserViewSchema(colander.MappingSchema):

    key = colander.SchemaNode(colander.String())

    class_name = colander.SchemaNode(colander.String())

    description = colander.SchemaNode(colander.String())

    # include_comments = colander.SchemaNode(colander.Bool())


def defaults(config, **kwargs):
    base = globals()

    PoserViewView = kwargs.get('PoserViewView', base['PoserViewView'])
    PoserViewView.defaults(config)


def includeme(config):
    defaults(config)
