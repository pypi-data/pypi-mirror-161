## -*- coding: utf-8 -*-
<%inherit file="/principal/find_by_perm.mako" />

<%def name="principal_table()">
  <table>
    <thead>
      <tr>
        <th>Username</th>
        <th>Person</th>
      </tr>
    </thead>
    <tbody>
      % for user in principals:
          <tr>
            <td>${h.link_to(user.username, url('users.view', uuid=user.uuid))}</td>
            <td>${user.person or ''}</td>
          </tr>
      % endfor
    </tbody>
  </table>
</%def>

${parent.body()}
