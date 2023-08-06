## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('rollover'):
      <li>${h.link_to("Yearly Rollover", url('{}.rollover'.format(route_prefix)))}</li>
  % endif
</%def>


${parent.body()}
