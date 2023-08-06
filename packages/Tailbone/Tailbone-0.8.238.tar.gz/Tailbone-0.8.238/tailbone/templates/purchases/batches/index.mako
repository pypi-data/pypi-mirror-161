## -*- coding: utf-8; -*-
<%inherit file="/batch/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('purchases.batch'):
      <li>${h.link_to("Go to Purchases", url('purchases'))}</li>
  % endif
</%def>

${parent.body()}
