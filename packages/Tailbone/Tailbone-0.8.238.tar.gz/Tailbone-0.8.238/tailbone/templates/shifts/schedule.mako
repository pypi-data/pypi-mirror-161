## -*- coding: utf-8 -*-
<%inherit file="/shifts/base.mako" />

<%def name="context_menu()">
  % if request.has_perm('schedule.edit'):
      <li>${h.link_to("Edit Schedule", url('schedule.edit'))}</li>
  % endif
  % if request.has_perm('schedule.print'):
      % if employee is Undefined:
          <li>${h.link_to("Print Schedule", url('schedule.print'), target='_blank')}</li>
      % else:
          <li>${h.link_to("Print this Schedule", url('schedule.employee.print'), target='_blank')}</li>
      % endif
  % endif
  % if request.has_perm('timesheet.view'):
      <li>${h.link_to("View this Time Sheet", url('schedule.goto.timesheet'), class_='goto')}</li>
  % endif
</%def>

<%def name="render_day(day)">
  % for shift in day['scheduled_shifts']:
      <p class="shift">${render_shift(shift)}</p>
  % endfor
</%def>

<%def name="render_employee_total(employee)">
  ${employee.scheduled_hours_display}
</%def>

<%def name="render_employee_day_total(day)">
  ${day['scheduled_hours_display']}
</%def>


${parent.body()}
