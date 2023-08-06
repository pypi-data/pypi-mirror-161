## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="page_content()">
  ${parent.page_content()}
  % if not use_buefy:
  <h2>Employees</h2>

  % if employees:
      <p>The following employees are assigned to this department:</p>
      ${employees.render_grid()|n}
  % else:
      <p>No employees are assigned to this department.</p>
  % endif
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ${form.component_studly}Data.employeesData = ${json.dumps(employees_data)|n}

  </script>
</%def>

${parent.body()}
