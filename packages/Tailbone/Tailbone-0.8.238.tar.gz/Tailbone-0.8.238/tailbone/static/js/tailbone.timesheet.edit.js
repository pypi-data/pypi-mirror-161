
/************************************************************
 *
 * tailbone.timesheet.edit.js
 *
 * Common logic for editing time sheet / schedule data.
 *
 ************************************************************/


var editing_day = null;
var new_shift_id = 1;
var show_timepicker = true;


/*
 * Add a new shift entry to the editor dialog.
 * @param {boolean} focus - Whether to set focus to the start_time input
 *   element after adding the shift.
 * @param {string} uuid - UUID value for the shift, if applicable.
 * @param {string} start_time - Value for start_time input element.
 * @param {string} end_time - Value for end_time input element.
 */

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
    shift.children('input[name|="edit_start_time"]').val(start_time);
    shift.children('input[name|="edit_end_time"]').val(end_time);
    $('#day-editor .shifts').append(shift);

    // maybe trick timepicker into never showing itself
    var args = {showPeriod: true};
    if (! show_timepicker) {
        args.showOn = 'button';
        args.button = '#nevershow';
    }
    shift.children('input').timepicker(args);

    if (focus) {
        shift.children('input:first').focus();
    }
}


/**
 * Calculate the number of minutes between given the times.
 * @param {string} start_time - Value from start_time input element.
 * @param {string} end_time - Value from end_time input element.
 */
function calc_minutes(start_time, end_time) {
    var start = parseTime(start_time);
    var end = parseTime(end_time);
    if (start && end) {
        start = new Date(2000, 0, 1, start.hh, start.mm);
        end = new Date(2000, 0, 1, end.hh, end.mm);
        return Math.floor((end - start) / 1000 / 60);
    }
}


/**
 * Converts a number of minutes into string of HH:MM format.
 * @param {number} minutes - Number of minutes to be converted.
 */
function format_minutes(minutes) {
    var hours = Math.floor(minutes / 60);
    if (hours) {
        minutes -= hours * 60;
    }
    return hours.toString() + ':' + (minutes < 10 ? '0' : '') + minutes.toString();
}


/**
 * NOTE: most of this logic was stolen from http://stackoverflow.com/a/1788084
 *
 * Parse a time string and convert to simple object with hh and mm keys.
 * @param {string} time - Time value in 'HH:MM PP' format, or close enough.
 */
function parseTime(time) {
    if (time) {
        var part = time.match(/(\d+):(\d+)(?: )?(am|pm)?/i);
        if (part) {
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
    }
}


/**
 * Return a jQuery object containing the hidden start or end time input element
 * for the shift (i.e. within the *main* timesheet form).  This will create the
 * input if necessary.
 * @param {jQuery} shift - A jQuery object for the shift itself.
 * @param {string} type - Should be 'start' or 'end' only.
 */
function time_input(shift, type) {
    var input = shift.children('input[name|="' + type + '_time"]');
    if (! input.length) {
        input = $('<input type="hidden" name="' + type + '_time-' + shift.data('uuid') + '" />');
        shift.append(input);
    }
    return input;
}


/**
 * Update the weekly hour total for a given row (employee).
 * @param {jQuery} row - A jQuery object for the row to be updated.
 */
function update_row_hours(row) {
    var minutes = 0;
    row.find('.day .shift:not(.deleted)').each(function() {
        var time_range = $.trim($(this).children('span').text()).split(' - ');
        minutes += calc_minutes(time_range[0], time_range[1]);
    });
    row.children('.total').text(minutes ? format_minutes(minutes) : '0');
}


/**
 * Clean up user input within the editor dialog, e.g. '8:30am' => '08:30 AM'.
 * This also should ensure invalid input will become empty string.
 */
function cleanup_editor_input() {
    // TODO: is this hacky? invoking timepicker to format the time values
    // in all cases, to avoid "invalid format" from user input
    var backward = false;
    $('#day-editor .shifts .shift').each(function() {
        var start_time = $(this).children('input[name|="edit_start_time"]');
        var end_time = $(this).children('input[name|="edit_end_time"]');
        $.timepicker._setTime(start_time.data('timepicker'), start_time.val() || '??');
        $.timepicker._setTime(end_time.data('timepicker'), end_time.val() || '??');
        var t_start = parseTime(start_time.val());
        var t_end = parseTime(end_time.val());
        if (t_start && t_end) {
            if ((t_start.hh > t_end.hh) || ((t_start.hh == t_end.hh) && (t_start.mm > t_end.mm))) {
                alert("Start time falls *after* end time!  Please fix...");
                start_time.focus().select();
                backward = true;
                return false;
            }
        }
    });
    return !backward;
}


/**
 * Update the main timesheet table based on editor dialog input.  This updates
 * both the displayed timesheet, as well as any hidden input elements on the
 * main form.
 */
function update_timetable() {

    var date = weekdays[editing_day.get(0).cellIndex - 1];

    // add or update
    $('#day-editor .shifts .shift').each(function() {
        var uuid = $(this).data('uuid');
        var start_time = $(this).children('input[name|="edit_start_time"]').val();
        var end_time = $(this).children('input[name|="edit_end_time"]').val();
        var shift = editing_day.children('.shift[data-uuid="' + uuid + '"]');
        if (! shift.length) {
            if (! (start_time || end_time)) {
                return;
            }
            shift = $('<p class="shift" data-uuid="' + uuid + '"><span></span></p>');
            shift.append($('<input type="hidden" name="employee_uuid-' + uuid + '" value="'
                           + editing_day.parents('tr:first').data('employee-uuid') + '" />'));
            editing_day.append(shift);
        }
        shift.children('span').text((start_time || '??') + ' - ' + (end_time || '??'));
        start_time = start_time ? (date + ' ' + start_time) : '';
        end_time = end_time ? (date + ' ' + end_time) : '';
        time_input(shift, 'start').val(start_time);
        time_input(shift, 'end').val(end_time);
    });


    // remove / mark for deletion
    editing_day.children('.shift').each(function() {
        var uuid = $(this).data('uuid');
        if (! $('#day-editor .shifts .shift[data-uuid="' + uuid + '"]').length) {
            if (uuid.match(/^new-/)) {
                $(this).remove();
            } else {
                $(this).addClass('deleted');
                $(this).append($('<input type="hidden" name="delete-' + uuid + '" value="delete" />'));
            }
        }
    });

}


/**
 * Perform full "save" action for time sheet form, direct from day editor dialog.
 */
function save_dialog() {
    if (! cleanup_editor_input()) {
        return false;
    }
    var save = $('#day-editor').parents('.ui-dialog').find('.ui-dialog-buttonpane button:first');
    save.button('disable').button('option', 'label', "Saving...");
    update_timetable();
    $('#timetable-form').submit();
    return true;
}


/*
 * on document load...
 */
$(function() {

    /*
     * Within editor dialog, clicking Add Shift button will create a new/empty
     * shift and set focus to its start_time input.
     */
    $('#day-editor #add-shift').click(function() {
        add_shift(true);
    });

    /*
     * Within editor dialog, clicking a shift's "trash can" button will remove
     * the shift.
     */
    $('#day-editor').on('click', '.shifts button', function() {
        $(this).parents('.shift:first').remove();
    });

    /*
     * Within editor dialog, Enter press within time field "might" trigger
     * save.  Note that this is only done for timesheet editing, not schedule.
     */
    $('#day-editor').on('keydown', '.shifts input[type="text"]', function(event) {
        if (!show_timepicker) { // TODO: this implies too much, should be cleaner
            if (event.which == 13) {
                save_dialog();
                return false;
            }
        }
    });

});
