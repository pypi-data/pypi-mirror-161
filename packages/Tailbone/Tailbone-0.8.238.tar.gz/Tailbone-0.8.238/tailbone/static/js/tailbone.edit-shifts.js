
/************************************************************
 *
 * tailbone.edit-shifts.js
 *
 * Common logic for editing time sheet / schedule data.
 *
 ************************************************************/


var editing_day = null;
var new_shift_id = 1;

function add_shift(focus, uuid, start_time, end_time) {
    var shift = $('#snippets .shift').clone();
    if (! uuid) {
        uuid = 'new-' + (new_shift_id++).toString();
    }
    shift.attr('data-uuid', uuid);
    shift.children('input').each(function() {
        var name = $(this).attr('name') + '-' + uuid;
        $(this).attr('name', name);
        $(this).attr('id', name);
    });
    shift.children('input[name|="edit_start_time"]').val(start_time || '');
    shift.children('input[name|="edit_end_time"]').val(end_time || '');
    $('#day-editor .shifts').append(shift);
    shift.children('input').timepicker({showPeriod: true});
    if (focus) {
        shift.children('input:first').focus();
    }
}

function calc_minutes(start_time, end_time) {
    var start = parseTime(start_time);
    start = new Date(2000, 0, 1, start.hh, start.mm);
    var end = parseTime(end_time);
    end = new Date(2000, 0, 1, end.hh, end.mm);
    return Math.floor((end - start) / 1000 / 60);
}

function format_minutes(minutes) {
    var hours = Math.floor(minutes / 60);
    if (hours) {
        minutes -= hours * 60;
    }
    return hours.toString() + ':' + (minutes < 10 ? '0' : '') + minutes.toString();
}

// stolen from http://stackoverflow.com/a/1788084
function parseTime(s) {
    var part = s.match(/(\d+):(\d+)(?: )?(am|pm)?/i);
    var hh = parseInt(part[1], 10);
    var mm = parseInt(part[2], 10);
    var ap = part[3] ? part[3].toUpperCase() : null;
    if (ap == 'AM') {
        if (hh == 12) {
            hh = 0;
        }
    } else if (ap == 'PM') {
        if (hh != 12) {
            hh += 12;
        }
    }
    return { hh: hh, mm: mm };
}

function time_input(shift, type) {
    var input = shift.children('input[name|="' + type + '_time"]');
    if (! input.length) {
        input = $('<input type="hidden" name="' + type + '_time-' + shift.data('uuid') + '" />');
        shift.append(input);
    }
    return input;
}

function update_row_hours(row) {
    var minutes = 0;
    row.find('.day .shift:not(.deleted)').each(function() {
        var time_range = $.trim($(this).children('span').text()).split(' - ');
        minutes += calc_minutes(time_range[0], time_range[1]);
    });
    row.children('.total').text(minutes ? format_minutes(minutes) : '0');
}

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
            var time_range = $.trim($(this).children('span').text()).split(' - ');
            add_shift(false, uuid, time_range[0], time_range[1]);
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
                    text: "Update",
                    click: function() {

                        // TODO: is this hacky? invoking timepicker to format the time values
                        // in all cases, to avoid "invalid format" from user input
                        editor.find('.shifts .shift').each(function() {
                            var start_time = $(this).children('input[name|="edit_start_time"]');
                            var end_time = $(this).children('input[name|="edit_end_time"]');
                            $.timepicker._setTime(start_time.data('timepicker'), start_time.val());
                            $.timepicker._setTime(end_time.data('timepicker'), end_time.val());
                        });

                        // create / update shifts in time table, as needed
                        editor.find('.shifts .shift').each(function() {
                            var uuid = $(this).data('uuid');
                            var start_time = $(this).children('input[name|="edit_start_time"]').val();
                            var end_time = $(this).children('input[name|="edit_end_time"]').val();
                            var shift = editing_day.children('.shift[data-uuid="' + uuid + '"]');
                            if (! shift.length) {
                                shift = $('<p class="shift" data-uuid="' + uuid + '"><span></span></p>');
                                shift.append($('<input type="hidden" name="employee_uuid-' + uuid + '" value="'
                                               + editing_day.parents('tr:first').data('employee-uuid') + '" />'));
                                editing_day.append(shift);
                            }
                            shift.children('span').text(start_time + ' - ' + end_time);
                            time_input(shift, 'start').val(date + ' ' + start_time);
                            time_input(shift, 'end').val(date + ' ' + end_time);
                        });

                        // remove shifts from time table, as needed
                        editing_day.children('.shift').each(function() {
                            var uuid = $(this).data('uuid');
                            if (! editor.find('.shifts .shift[data-uuid="' + uuid + '"]').length) {
                                if (uuid.match(/^new-/)) {
                                    $(this).remove();
                                } else {
                                    $(this).addClass('deleted');
                                    $(this).append($('<input type="hidden" name="delete-' + uuid + '" value="delete" />'));
                                }
                            }
                        });

                        // mark day as modified, close dialog
                        editing_day.addClass('modified');
                        $('.save-changes').button('enable');
                        $('.undo-changes').button('enable');
                        update_row_hours(editing_day.parents('tr:first'));
                        editor.dialog('close');
                        data_modified = true;
                        okay_to_leave = false;
                    }
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

    $('#day-editor #add-shift').click(function() {
        add_shift(true);
    });

    $('#day-editor').on('click', '.shifts button', function() {
        $(this).parents('.shift:first').remove();
    });

    $('.save-changes').click(function() {
        $(this).button('disable').button('option', 'label', "Saving Changes...");
        okay_to_leave = true;
        $('#timetable-form').submit();
    });

    $('.undo-changes').click(function() {
        $(this).button('disable').button('option', 'label', "Refreshing...");
        okay_to_leave = true;
        location.href = location.href;
    });

});
