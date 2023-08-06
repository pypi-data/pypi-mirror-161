## -*- coding: utf-8 -*-
<%inherit file="/shifts/base.mako" />

<%def name="context_menu()">
    % if employee is not Undefined and request.has_perm('timesheet.edit'):
        <li>${h.link_to("Edit this Time Sheet", url('timesheet.employee.edit'))}</li>
    % endif
    % if request.has_perm('schedule.view'):
        <li>${h.link_to("View this Schedule", url('timesheet.goto.schedule'), class_='goto')}</li>
    % endif
</%def>

<%def name="render_day(day)">
  % for shift in day['worked_shifts']:
      <p class="shift">${render_shift(shift)}</p>
  % endfor
</%def>

<%def name="render_employee_total(employee)">
  ${employee.worked_hours_display}
</%def>

<%def name="render_employee_day_total(day)">
  <span title="${h.hours_as_decimal(day['worked_hours'])} hrs">${day['worked_hours_display']}</span>
</%def>


${self.timesheet_wrapper()}
