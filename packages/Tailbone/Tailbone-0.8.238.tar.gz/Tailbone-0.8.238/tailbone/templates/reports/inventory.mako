## -*- coding: utf-8 -*-
<%inherit file="/reports/base.mako" />

<%def name="title()">Report : Inventory Worksheet</%def>

<p>Please provide the following criteria to generate your report:</p>
<br />

${h.form(request.current_route_url())}
${h.csrf_token(request)}

<div class="field-wrapper">
  <label for="department">Department</label>
  <div class="field">
    <select name="department">
      % for department in departments:
          <option value="${department.uuid}">${department.name}</option>
      % endfor
    </select>
  </div>
</div>

<div class="field-wrapper">
  ${h.checkbox('weighted-only', label="Only include items which are sold by weight.")}
</div>

<div class="field-wrapper">
  ${h.checkbox('exclude-not-for-sale', label="Exclude items marked \"not for sale\".", checked=True)}
</div>

<div class="buttons">
  ${h.submit('submit', "Generate Report")}
</div>

${h.end_form()}
