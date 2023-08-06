## -*- coding: utf-8 -*-
<%inherit file="/shifts/base.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  ${self.edit_timetable_javascript()}
  <script type="text/javascript">

    $(function() {

        % if allow_clear:
        $('.clear-schedule').click(function() {
            if (confirm("This will remove all shifts from the schedule you're " +
                        "currently viewing.\n\nAre you sure you wish to do this?")) {
                $(this).button('disable').button('option', 'label', "Clearing...");
                okay_to_leave = true;
                $('#clear-schedule-form').submit();
            }
        });
        % endif

        $('#copy-week').datepicker({
            dateFormat: 'mm/dd/yy'
        });

        $('.copy-schedule').click(function() {
            $('#copy-details').dialog({
                modal: true,
                title: "Copy from Another Week",
                width: '500px',
                buttons: [
                    {
                        text: "Copy Schedule",
                        click: function(event) {
                            if (! $('#copy-week').val()) {
                                alert("You must specify the week from which to copy shift data.");
                                $('#copy-week').focus();
                                return;
                            }
                            disable_button(dialog_button(event), "Copying Schedule");
                            $('#copy-schedule-form').submit();
                        }
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            $('#copy-details').dialog('close');
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
  % if request.has_perm('schedule.viewall'):
      <li>${h.link_to("View Schedule", url('schedule'))}</li>
  % endif
  % if request.has_perm('schedule.print'):
      <li>${h.link_to("Print Schedule", url('schedule.print'), target='_blank')}</li>
  % endif
</%def>

<%def name="render_day(day)">
  % for shift in day['scheduled_shifts']:
      <p class="shift" data-uuid="${shift.uuid}">
        ${render_shift(shift)}
      </p>
  % endfor
</%def>

<%def name="render_employee_total(employee)">
  ${employee.scheduled_hours_display}
</%def>

<%def name="edit_form()">
  ${h.form(url('schedule.edit'), id='timetable-form')}
  ${h.csrf_token(request)}
</%def>

<%def name="edit_tools()">
  <div class="buttons">
    <button type="button" class="save-changes" disabled="disabled">Save Changes</button>
    <button type="button" class="undo-changes" disabled="disabled">Undo Changes</button>
    % if allow_clear:
    <button type="button" class="clear-schedule">Clear Schedule</button>
    % endif
    <button type="button" class="copy-schedule">Copy Schedule From...</button>
  </div>
</%def>


${self.timesheet_wrapper(with_edit_form=True)}

${edit_tools()}

% if allow_clear:
${h.form(url('schedule.edit'), id="clear-schedule-form")}
${h.csrf_token(request)}
${h.hidden('clear-schedule', value='clear')}
${h.end_form()}
% endif

<div id="day-editor" style="display: none;">
  <div class="shifts"></div>
  <button type="button" id="add-shift">Add Shift</button>
</div>

<div id="copy-details" style="display: none;">
  <p>
    This tool will replace the currently visible schedule, with one from
    another week.
  </p>
  <p>
    <strong>NOTE:</strong>&nbsp; If you do this, all shifts in the current
    schedule will be <em>removed</em>,
    and then new shifts will be created based on the week you specify.
  </p>
  ${h.form(url('schedule.edit'), id='copy-schedule-form')}
  ${h.csrf_token(request)}
  <label for="copy-week">Copy from week:</label>
  ${h.text('copy-week')}
  ${h.end_form()}
</div>

<div id="snippets">
  <div class="shift" data-uuid="">
    ${h.text('edit_start_time')} thru ${h.text('edit_end_time')}
    <button type="button"><span class="ui-icon ui-icon-trash"></span></button>
  </div>
</div>
