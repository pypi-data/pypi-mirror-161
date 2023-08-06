
/************************************************************
 *
 * tailbone.js
 *
 ************************************************************/


/*
 * Initialize the disabled filters array.  This is populated from within the
 * /grids/search.mako template.
 */
var filters_to_disable = [];


/*
 * Disables options within the "add filter" dropdown which correspond to those
 * filters already being displayed.  Called from /grids/search.mako template.
 */
function disable_filter_options() {
    while (filters_to_disable.length) {
        var filter = filters_to_disable.shift();
        var option = $('#add-filter option[value="' + filter + '"]');
        option.attr('disabled', 'disabled');
    }
}


/*
 * Convenience function to disable a UI button.
 */
function disable_button(button, label) {
    $(button).button('disable');
    if (label === undefined) {
        label = $(button).data('working-label') || "Working, please wait...";
    }
    if (label) {
        if (label.slice(-3) != '...') {
            label += '...';
        }
        $(button).button('option', 'label', label);
    }
}


function disable_submit_button(form, label) {
    // for some reason chrome requires us to do things this way...
    // https://stackoverflow.com/questions/16867080/onclick-javascript-stops-form-submit-in-chrome
    // https://stackoverflow.com/questions/5691054/disable-submit-button-on-form-submit
    var submit = $(form).find('input[type="submit"]');
    if (! submit.length) {
        submit = $(form).find('button[type="submit"]');
    }
    if (submit.length) {
        disable_button(submit, label);
    }
}


/*
 * Load next / previous page of results to grid.  This function is called on
 * the click event from the pager links, via inline script code.
 */
function grid_navigate_page(link, url) {
    var wrapper = $(link).parents('div.grid-wrapper');
    var grid = wrapper.find('div.grid');
    wrapper.mask("Loading...");
    $.get(url, function(data) {
        wrapper.unmask();
        grid.replaceWith(data);
    });
}


/*
 * Fetch the UUID value associated with a table row.
 */
function get_uuid(obj) {
    obj = $(obj);
    if (obj.attr('uuid')) {
        return obj.attr('uuid');
    }
    var tr = obj.parents('tr:first');
    if (tr.attr('uuid')) {
        return tr.attr('uuid');
    }
    return undefined;
}


/*
 * Return a jQuery object containing a button from a dialog.  This is a
 * convenience function to help with browser differences.  It is assumed
 * that it is being called from within the relevant button click handler.
 * @param {event} event - Click event object.
 */
function dialog_button(event) {
    var button = $(event.target);

    // TODO: not sure why this workaround is needed for Chrome..?
    if (! button.hasClass('ui-button')) {
        button = button.parents('.ui-button:first');
    }

    return button;
}


/**
 * Scroll screen as needed to ensure all options are visible, for the given
 * select menu widget.
 */
function show_all_options(select) {
    if (! select.is(':visible')) {
        /*
         * Note that the following code was largely stolen from
         * http://brianseekford.com/2013/06/03/how-to-scroll-a-container-or-element-into-view-using-jquery-javascript-in-your-html/
         */

        var docViewTop = $(window).scrollTop();
        var docViewBottom = docViewTop + $(window).height();

        var widget = select.selectmenu('menuWidget');
        var elemTop = widget.offset().top;
        var elemBottom = elemTop + widget.height();

        var isScrolled = ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));

        if (!isScrolled) {
            if (widget.height() > $(window).height()) { //then just bring to top of the container
                $(window).scrollTop(elemTop)
            } else { //try and and bring bottom of container to bottom of screen
                $(window).scrollTop(elemTop -  ($(window).height() - widget.height()));
            }
        }
    }
}


/*
 * reference to existing timeout warning dialog, if any
 */
var session_timeout_warning = null;


/**
 * Warn user of impending session timeout.
 */
function timeout_warning() {
    if (! session_timeout_warning) {
        session_timeout_warning = $('<div id="session-timeout-warning">' +
                                    'You will be logged out in <span class="seconds"></span> ' +
                                    'seconds...</div>');
    }
    session_timeout_warning.find('.seconds').text('60');
    session_timeout_warning.dialog({
        title: "Session Timeout Warning",
        modal: true,
        buttons: {
            "Stay Logged In": function() {
                session_timeout_warning.dialog('close');
                $.get(noop_url, set_timeout_warning_timer);
            },
            "Logout Now": function() {
                location.href = logout_url;
            }
        }
    });
    window.setTimeout(timeout_warning_update, 1000);
}


/**
 * Decrement the 'seconds' counter for the current timeout warning
 */
function timeout_warning_update() {
    if (session_timeout_warning.is(':visible')) {
        var span = session_timeout_warning.find('.seconds');
        var seconds = parseInt(span.text()) - 1;
        if (seconds) {
            span.text(seconds.toString());
            window.setTimeout(timeout_warning_update, 1000);
        } else {
            location.href = logout_url;
        }
    }
}


/**
 * Warn user of impending session timeout.
 */
function set_timeout_warning_timer() {
    // timout dialog says we're 60 seconds away, but we actually trigger when
    // 70 seconds away from supposed timeout, in case of timer drift?
    window.setTimeout(timeout_warning, session_timeout * 1000 - 70000);
}


/*
 * set initial timer for timeout warning, if applicable
 */
if (session_timeout) {
    set_timeout_warning_timer();
}


$(function() {

    /*
     * enhance buttons
     */
    $('button, a.button').button();
    $('input[type=submit]').button();
    $('input[type=reset]').button();
    $('a.button.autodisable').click(function() {
        disable_button(this);
    });
    $('form.autodisable').submit(function() {
        disable_submit_button(this);
    });

    // quickie button
    $('#submit-quickie').button('option', 'icons', {primary: 'ui-icon-zoomin'});

    /*
     * enhance dropdowns
     */
    $('select[auto-enhance="true"]').selectmenu();
    $('select[auto-enhance="true"]').on('selectmenuopen', function(event, ui) {
        show_all_options($(this));
    });

    /* Also automatically disable any buttons marked for that. */
    $('a.button[disabled=disabled]').button('option', 'disabled', true);

    /*
     * Apply timepicker behavior to text inputs which are marked for it.
     */
    $('input[type=text].timepicker').timepicker({
        showPeriod: true
    });

    /*
     * When filter labels are clicked, (un)check the associated checkbox.
     */
    $('body').on('click', '.grid-wrapper .filter label', function() {
        var checkbox = $(this).prev('input[type="checkbox"]');
        if (checkbox.prop('checked')) {
            checkbox.prop('checked', false);
            return false;
        }
        checkbox.prop('checked', true);
    });

    /*
     * When a new filter is selected in the "add filter" dropdown, show it in
     * the UI.  This selects the filter's checkbox and puts focus to its input
     * element.  If all available filters have been displayed, the "add filter"
     * dropdown will be hidden.
     */
    $('body').on('change', '#add-filter', function() {
        var select = $(this);
        var filters = select.parents('div.filters:first');
        var filter = filters.find('#filter-' + select.val());
        var checkbox = filter.find('input[type="checkbox"]:first');
        var input = filter.find(':last-child');

        checkbox.prop('checked', true);
        filter.show();
        input.select();
        input.focus();

        filters.find('input[type="submit"]').show();
        filters.find('button[type="reset"]').show();

        select.find('option:selected').attr('disabled', true);
        select.val('add a filter');
        if (select.find('option:enabled').length == 1) {
            select.hide();
        }
    });

    /*
     * When user clicks the grid filters search button, perform the search in
     * the background and reload the grid in-place.
     */
    $('body').on('submit', '.filters form', function() {
        var form = $(this);
        var wrapper = form.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = form.serializeArray();
        data.push({name: 'partial', value: true});
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });
        return false;
    });

    /*
     * When user clicks the grid filters reset button, manually clear all
     * filter input elements, and submit a new search.
     */
    $('body').on('click', '.filters form button[type="reset"]', function() {
        var form = $(this).parents('form');
        form.find('div.filter').each(function() {
            $(this).find('div.value input').val('');
        });
        form.submit();
        return false;
    });

    $('body').on('click', '.grid thead th.sortable a', function() {
        var th = $(this).parent();
        var wrapper = th.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = {
            sort: th.attr('field'),
            dir: (th.hasClass('sorted') && th.hasClass('asc')) ? 'desc' : 'asc',
            page: 1,
            partial: true
        };
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });
        return false;
    });

    $('body').on('mouseenter', '.grid.hoverable tbody tr', function() {
        $(this).addClass('hovering');
    });

    $('body').on('mouseleave', '.grid.hoverable tbody tr', function() {
        $(this).removeClass('hovering');
    });

    $('body').on('click', '.grid tbody td.view', function() {
        var url = $(this).attr('url');
        if (url) {
            location.href = url;
        }
    });

    $('body').on('click', '.grid tbody td.edit', function() {
        var url = $(this).attr('url');
        if (url) {
            location.href = url;
        }
    });

    $('body').on('click', '.grid tbody td.delete', function() {
        var url = $(this).attr('url');
        if (url) {
            if (confirm("Do you really wish to delete this object?")) {
                location.href = url;
            }
        }
    });

    // $('div.grid-wrapper').on('change', 'div.grid div.pager select#grid-page-count', function() {
    $('body').on('change', '.grid .pager #grid-page-count', function() {
        var select = $(this);
        var wrapper = select.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = {
            per_page: select.val(),
            partial: true
        };
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });

    });
    
    $('body').on('click', 'div.dialog button.close', function() {
        var dialog = $(this).parents('div.dialog:first');
        dialog.dialog('close');
    });

});
