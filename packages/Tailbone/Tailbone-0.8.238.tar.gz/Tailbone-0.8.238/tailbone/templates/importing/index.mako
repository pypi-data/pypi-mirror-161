## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="render_grid_component()">
  <p class="block">
    ${request.rattail_config.get_app().get_title()} can run import / export jobs for the following:
  </p>
  ${parent.render_grid_component()}
</%def>


${parent.body()}
