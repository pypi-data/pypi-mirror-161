## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('{}.find_by_perm'.format(permission_prefix)):
      <li>${h.link_to("Find {} with Permission X".format(model_title_plural), url('{}.find_by_perm'.format(route_prefix)))}</li>
  % endif
</%def>

${parent.body()}
