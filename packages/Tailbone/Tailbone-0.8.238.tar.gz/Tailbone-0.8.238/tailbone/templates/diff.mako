## -*- coding: utf-8; -*-
<table class="diff dirty${' monospace' if diff.monospace else ''}">
  <thead>
    <tr>
      % for column in diff.columns:
          <th>${column}</th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for field in diff.fields:
       <tr ${diff.get_row_attrs(field)|n}>
         <td class="field">${diff.render_field(field)}</td>
         <td class="old-value">${diff.render_old_value(field)}</td>
         <td class="new-value">${diff.render_new_value(field)}</td>
       </tr>
    % endfor
  </tbody>
</table>
