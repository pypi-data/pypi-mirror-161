## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">${model_title}</%def>

<%def name="content_title()">
  ${row_title}
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {}".format(parent_model_title), instance_url)}</li>
  % if master.rows_editable and instance_editable and request.has_perm('{}.edit'.format(permission_prefix)):
      <li>${h.link_to("Edit this {}".format(model_title), action_url('edit', instance))}</li>
  % endif
  % if not use_buefy and instance_deletable and master.has_perm('delete_row'):
      <li>${h.link_to("Delete this {}".format(model_title), action_url('delete', instance))}</li>
  % endif
  % if rows_creatable and request.has_perm('{}.create'.format(permission_prefix)):
      <li>${h.link_to("Create a new {}".format(model_title), url('{}.create'.format(route_prefix)))}</li>
  % endif
</%def>


${parent.body()}
