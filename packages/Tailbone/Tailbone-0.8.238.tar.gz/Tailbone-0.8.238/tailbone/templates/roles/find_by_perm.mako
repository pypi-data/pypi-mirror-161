## -*- coding: utf-8 -*-
<%inherit file="/principal/find_by_perm.mako" />

<%def name="principal_table()">
  <table>
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
      % for role in principals:
          <tr>
            <td>${h.link_to(role.name, url('roles.view', uuid=role.uuid))}</td>
          </tr>
      % endfor
    </tbody>
  </table>
</%def>

${parent.body()}
