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
App Menus
"""

from __future__ import unicode_literals, absolute_import

import re
import logging

from rattail.util import import_module_path, prettify, simple_error

from webhelpers2.html import tags, HTML

from tailbone.db import Session


log = logging.getLogger(__name__)


def make_simple_menus(request):
    """
    Build the main menu list for the app.
    """
    # first try to make menus from config, but this is highly
    # susceptible to failure, so try to warn user of problems
    raw_menus = None
    try:
        raw_menus = make_menus_from_config(request)
    except Exception as error:
        # TODO: these messages show up multiple times on some pages?!
        # that must mean the BeforeRender event is firing multiple
        # times..but why??  seems like there is only 1 request...
        log.warning("failed to make menus from config", exc_info=True)
        request.session.flash(simple_error(error), 'error')
        request.session.flash("Menu config is invalid! Reverting to menus "
                              "defined in code!", 'warning')
        msg = HTML.literal('Please edit your {} ASAP.'.format(
            tags.link_to("Menu Config", request.route_url('configure_menus'))))
        request.session.flash(msg, 'warning')

    if not raw_menus:

        # no config, so import/invoke code function to build them
        menus_module = import_module_path(
            request.rattail_config.require('tailbone', 'menus'))
        if not hasattr(menus_module, 'simple_menus') or not callable(menus_module.simple_menus):
            raise RuntimeError("module does not have a simple_menus() callable: {}".format(menus_module))
        raw_menus = menus_module.simple_menus(request)

    # now we have "simple" (raw) menus definition, but must refine
    # that somewhat to produce our final menus
    mark_allowed(request, raw_menus)
    final_menus = []
    for topitem in raw_menus:

        if topitem['allowed']:

            if topitem.get('type') == 'link':
                final_menus.append(make_menu_entry(request, topitem))

            else: # assuming 'menu' type

                menu_items = []
                for item in topitem['items']:
                    if not item['allowed']:
                        continue

                    # nested submenu
                    if item.get('type') == 'menu':
                        submenu_items = []
                        for subitem in item['items']:
                            if subitem['allowed']:
                                submenu_items.append(make_menu_entry(request, subitem))
                        menu_items.append({
                            'type': 'submenu',
                            'title': item['title'],
                            'items': submenu_items,
                            'is_menu': True,
                            'is_sep': False,
                        })

                    elif item.get('type') == 'sep':
                        # we only want to add a sep, *if* we already have some
                        # menu items (i.e. there is something to separate)
                        # *and* the last menu item is not a sep (avoid doubles)
                        if menu_items and not menu_items[-1]['is_sep']:
                            menu_items.append(make_menu_entry(request, item))

                    else: # standard menu item
                        menu_items.append(make_menu_entry(request, item))

                # remove final separator if present
                if menu_items and menu_items[-1]['is_sep']:
                    menu_items.pop()

                # only add if we wound up with something
                assert menu_items
                if menu_items:
                    group = {
                        'type': 'menu',
                        'key': topitem.get('key'),
                        'title': topitem['title'],
                        'items': menu_items,
                        'is_menu': True,
                        'is_link':  False,
                    }

                    # topitem w/ no key likely means it did not come
                    # from config but rather explicit definition in
                    # code.  so we are free to "invent" a (safe) key
                    # for it, since that is only for editing config
                    if not group['key']:
                        group['key'] = make_menu_key(request.rattail_config,
                                                     topitem['title'])

                    final_menus.append(group)

    return final_menus


def make_menus_from_config(request):
    """
    Try to build a complete menu set from config/settings.

    This essentially checks for the top-level menu list in config; if
    found then it will build a full menu set from config.  If this
    top-level list is not present in config then menus will be built
    purely from code instead.  An example of this top-level list:

    .. code-hightlight:: ini

       [tailbone.menu]
       menus = first, second, third, admin

    Obviously much more config would be needed to define those menus
    etc. but that is the option that determines whether the rest of
    menu config is even read, or not.
    """
    config = request.rattail_config
    main_keys = config.getlist('tailbone.menu', 'menus')
    if not main_keys:
        return

    menus = []

    # menu definition can come either from config file or db settings,
    # but if the latter then we want to optimize with one big query
    if config.getbool('tailbone.menu', 'from_settings',
                      default=False):
        app = config.get_app()
        model = config.get_model()

        # fetch all menu-related settings at once
        query = Session().query(model.Setting)\
                         .filter(model.Setting.name.like('tailbone.menu.%'))
        settings = app.cache_model(Session(), model.Setting,
                                   query=query, key='name',
                                   normalizer=lambda s: s.value)
        for key in main_keys:
            menus.append(make_single_menu_from_settings(request, key, settings))

    else: # read from config file only
        for key in main_keys:
            menus.append(make_single_menu_from_config(request, key))

    return menus


def make_single_menu_from_config(request, key):
    """
    Makes a single top-level menu dict from config file.  Note that
    this will read from config file(s) *only* and avoids querying the
    database, for efficiency.
    """
    config = request.rattail_config
    menu = {
        'key': key,
        'type': 'menu',
        'items': [],
    }

    # title
    title = config.get('tailbone.menu',
                       'menu.{}.label'.format(key),
                       usedb=False)
    menu['title'] = title or prettify(key)

    # items
    item_keys = config.getlist('tailbone.menu',
                               'menu.{}.items'.format(key),
                               usedb=False)
    for item_key in item_keys:
        item = {}

        if item_key == 'SEP':
            item['type'] = 'sep'

        else:
            item['type'] = 'item'
            item['key'] = item_key

            # title
            title = config.get('tailbone.menu',
                               'menu.{}.item.{}.label'.format(key, item_key),
                               usedb=False)
            item['title'] = title or prettify(item_key)

            # route
            route = config.get('tailbone.menu',
                               'menu.{}.item.{}.route'.format(key, item_key),
                               usedb=False)
            if route:
                item['route'] = route
                item['url'] = request.route_url(route)

            else:

                # url
                url = config.get('tailbone.menu',
                                 'menu.{}.item.{}.url'.format(key, item_key),
                                 usedb=False)
                if not url:
                    url = request.route_url(item_key)
                elif url.startswith('route:'):
                    url = request.route_url(url[6:])
                item['url'] = url

            # perm
            perm = config.get('tailbone.menu',
                              'menu.{}.item.{}.perm'.format(key, item_key),
                              usedb=False)
            item['perm'] = perm or '{}.list'.format(item_key)

        menu['items'].append(item)

    return menu


def make_single_menu_from_settings(request, key, settings):
    """
    Makes a single top-level menu dict from DB settings.
    """
    config = request.rattail_config
    menu = {
        'key': key,
        'type': 'menu',
        'items': [],
    }

    # title
    title = settings.get('tailbone.menu.menu.{}.label'.format(key))
    menu['title'] = title or prettify(key)

    # items
    item_keys = config.parse_list(
        settings.get('tailbone.menu.menu.{}.items'.format(key)))
    for item_key in item_keys:
        item = {}

        if item_key == 'SEP':
            item['type'] = 'sep'

        else:
            item['type'] = 'item'
            item['key'] = item_key

            # title
            title = settings.get('tailbone.menu.menu.{}.item.{}.label'.format(
                key, item_key))
            item['title'] = title or prettify(item_key)

            # route
            route = settings.get('tailbone.menu.menu.{}.item.{}.route'.format(
                key, item_key))
            if route:
                item['route'] = route
                item['url'] = request.route_url(route)

            else:

                # url
                url = settings.get('tailbone.menu.menu.{}.item.{}.url'.format(
                    key, item_key))
                if not url:
                    url = request.route_url(item_key)
                if url.startswith('route:'):
                    url = request.route_url(url[6:])
                item['url'] = url

            # perm
            perm = settings.get('tailbone.menu.menu.{}.item.{}.perm'.format(
                key, item_key))
            item['perm'] = perm or '{}.list'.format(item_key)

        menu['items'].append(item)

    return menu


def make_menu_key(config, value):
    """
    Generate a normalized menu key for the given value.
    """
    return re.sub(r'\W', '', value.lower())


def make_menu_entry(request, item):
    """
    Convert a simple menu entry dict, into a proper menu-related object, for
    use in constructing final menu.
    """
    # separator
    if item.get('type') == 'sep':
        return {
            'type': 'sep',
            'is_menu': False,
            'is_sep': True,
        }

    # standard menu item
    entry = {
        'type': 'item',
        'title': item['title'],
        'perm': item.get('perm'),
        'target': item.get('target'),
        'is_link': True,
        'is_menu': False,
        'is_sep': False,
    }
    if item.get('route'):
        entry['route'] = item['route']
        entry['url'] = request.route_url(entry['route'])
        entry['key'] = entry['route']
    else:
        if item.get('url'):
            entry['url'] = item['url']
        entry['key'] = make_menu_key(request.rattail_config, entry['title'])
    return entry


def is_allowed(request, item):
    """
    Logic to determine if a given menu item is "allowed" for current user.
    """
    perm = item.get('perm')
    if perm:
        return request.has_perm(perm)
    return True


def mark_allowed(request, menus):
    """
    Traverse the menu set, and mark each item as "allowed" (or not) based on
    current user permissions.
    """
    for topitem in menus:

        if topitem.get('type', 'menu') == 'menu':
            topitem['allowed'] = False

            for item in topitem['items']:

                if item.get('type') == 'menu':
                    for subitem in item['items']:
                        subitem['allowed'] = is_allowed(request, subitem)

                    item['allowed'] = False
                    for subitem in item['items']:
                        if subitem['allowed'] and subitem.get('type') != 'sep':
                            item['allowed'] = True
                            break

                else:
                    item['allowed'] = is_allowed(request, item)

            for item in topitem['items']:
                if item['allowed'] and item.get('type') != 'sep':
                    topitem['allowed'] = True
                    break
