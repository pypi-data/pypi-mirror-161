## -*- coding: utf-8; -*-
<%inherit file="/principal/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('download_permissions_matrix'):
      <li>${h.link_to("Download Permissions Matrix", url('roles.download_permissions_matrix'))}</li>
  % endif
</%def>


${parent.body()}
