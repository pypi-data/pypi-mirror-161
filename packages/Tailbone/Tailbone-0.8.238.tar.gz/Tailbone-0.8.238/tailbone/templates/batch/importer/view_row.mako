## -*- coding: utf-8; -*-
<%inherit file="/master/view_row.mako" />

<%def name="context_menu_items()">
  % if not batch.executed and request.has_perm('{}.delete_row'.format(permission_prefix)):
      <li>${h.link_to("Delete this Row", url('{}.delete_row'.format(route_prefix), uuid=batch.uuid, row_uuid=instance.uuid))}</li>
  % endif
</%def>

<%def name="field_diff_table()">
% if instance.status_code == enum.IMPORTER_BATCH_ROW_STATUS_CREATE:
    <table class="diff monospace new">
      <thead>
        <tr>
          <th>field name</th>
          <th>old value</th>
          <th>new value</th>
        </tr>
      </thead>
      <tbody>
        % for field in diff_fields:
           <tr>
             <td class="field">${field}</td>
             <td class="value old-value">&nbsp;</td>
             <td class="value new-value">${repr(diff_new_values[field])}</td>
           </tr>
        % endfor
      </tbody>
    </table>
% elif instance.status_code in (enum.IMPORTER_BATCH_ROW_STATUS_UPDATE, enum.IMPORTER_BATCH_ROW_STATUS_NOCHANGE):
    <table class="diff monospace dirty">
      <thead>
        <tr>
          <th>field name</th>
          <th>old value</th>
          <th>new value</th>
        </tr>
      </thead>
      <tbody>
        % for field in diff_fields:
           <tr${' class="diff"' if diff_new_values[field] != diff_old_values[field] else ''|n}>
             <td class="field">${field}</td>
             <td class="value old-value">${repr(diff_old_values[field])}</td>
             <td class="value new-value">${repr(diff_new_values[field])}</td>
           </tr>
        % endfor
      </tbody>
    </table>
% elif instance.status_code == enum.IMPORTER_BATCH_ROW_STATUS_DELETE:
    <table class="diff monospace deleted">
      <thead>
        <tr>
          <th>field name</th>
          <th>old value</th>
          <th>new value</th>
        </tr>
      </thead>
      <tbody>
        % for field in diff_fields:
           <tr>
             <td class="field">${field}</td>
             <td class="value old-value">${repr(diff_old_values[field])}</td>
             <td class="value new-value">&nbsp;</td>
           </tr>
        % endfor
      </tbody>
    </table>
% endif
</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <tailbone-form></tailbone-form>
    <br />
    ${self.field_diff_table()}
  </div>
</%def>

<%def name="render_form()">
  ${parent.render_form()}
  % if not use_buefy:
      ${self.field_diff_table()}
  % endif
</%def>


${parent.body()}
