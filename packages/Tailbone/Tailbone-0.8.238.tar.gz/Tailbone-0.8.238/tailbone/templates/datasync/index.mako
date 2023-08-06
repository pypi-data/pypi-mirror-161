## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('datasync_changes.list'):
      <li>${h.link_to("View DataSync Changes", url('datasyncchanges'))}</li>
  % endif
</%def>

<%def name="render_grid_component()">
  <b-notification :closable="false">
    TODO: this page coming soon...
  </b-notification>
  ${parent.render_grid_component()}
</%def>


${parent.body()}
