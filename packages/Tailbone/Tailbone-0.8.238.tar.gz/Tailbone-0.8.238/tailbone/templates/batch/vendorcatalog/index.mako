## -*- coding: utf-8; -*-
<%inherit file="/batch/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if h.route_exists(request, 'vendors') and request.has_perm('vendors.list'):
      <li>${h.link_to("View Vendors", url('vendors'))}</li>
  % endif
</%def>

${parent.body()}
