## -*- coding: utf-8; -*-
<%inherit file="/master/edit.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {}".format(parent_model_title), parent_url)}</li>
  % if master.rows_viewable and request.has_perm('{}.view'.format(row_permission_prefix)):
      <li>${h.link_to("View this {}".format(row_model_title), row_action_url('view', instance))}</li>
  % endif
  % if master.rows_deletable and instance_deletable and request.has_perm('{}.delete'.format(row_permission_prefix)):
      <li>${h.link_to("Delete this {}".format(row_model_title), row_action_url('delete', instance))}</li>
  % endif
  % if master.rows_creatable and request.has_perm('{}.create'.format(row_permission_prefix)):
      <li>${h.link_to("Create a new {}".format(row_model_title), url('{}.create_row'.format(route_prefix), uuid=row_parent.uuid))}</li>
  % endif
</%def>

${parent.body()}
