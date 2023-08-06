## -*- coding: utf-8 -*-
<%inherit file="/shifts/base.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.timesheet.edit.js'))}
  <script type="text/javascript">

    show_timepicker = false;

    $(function() {

        $('.timesheet').on('click', '.day', function() {
            editing_day = $(this);
            var editor = $('#day-editor');
            var employee = editing_day.siblings('.employee').text();
            var date = weekdays[editing_day.get(0).cellIndex - 1];
            var shifts = editor.children('.shifts');
            shifts.empty();
            editing_day.children('.shift:not(.deleted)').each(function() {
                var uuid = $(this).data('uuid');
                var times = $.trim($(this).children('span').text()).split(' - ');
                times[0] = times[0] == '??' ? '' : times[0];
                times[1] = times[1] == '??' ? '' : times[1];
                add_shift(false, uuid, times[0], times[1]);
            });
            if (! shifts.children('.shift').length) {
                add_shift();
            }
            editor.dialog({
                modal: true,
                title: employee + ' - ' + date,
                position: {my: 'center', at: 'center', of: editing_day},
                width: 'auto',
                autoResize: true,
                buttons: [
                    {
                        text: "Save Changes",
                        click: save_dialog
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            editor.dialog('close');
                        }
                    }
                ]
            });
        });

    });

  </script>
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${self.edit_timetable_styles()}
</%def>

<%def name="context_menu()">
  % if request.has_perm('timesheet.view'):
      <li>${h.link_to("View this Time Sheet", url('timesheet.employee'))}</li>
  % endif
  % if request.has_perm('schedule.view'):
      <li>${h.link_to("View this Schedule", url('schedule.employee'))}</li>
  % endif
</%def>

<%def name="render_day(day)">
  % for shift in day['worked_shifts']:
      <p class="shift" data-uuid="${shift.uuid}">
        ${render_shift(shift)}
      </p>
  % endfor
</%def>

<%def name="render_employee_total(employee)">
  ${employee.worked_hours_display}
</%def>

<%def name="render_employee_day_total(day)">
  ${day['worked_hours_display']}
</%def>

<%def name="edit_form()">
  ${h.form(url('timesheet.employee.edit'), id='timetable-form')}
  ${h.csrf_token(request)}
</%def>


${self.timesheet_wrapper(with_edit_form=True, change_employee='confirm_leave')}

<div id="day-editor" style="display: none;">
  <div class="shifts"></div>
  <button type="button" id="add-shift">Add Shift</button>
</div>

<div id="snippets">
  <div class="shift" data-uuid="">
    ${h.text('edit_start_time')} thru ${h.text('edit_end_time')}
    <button type="button"><span class="ui-icon ui-icon-trash"></span></button>
  </div>
</div>
