
/**********************************************************************
 * jQuery UI plugins for Tailbone
 **********************************************************************/

/**********************************************************************
 * gridcore plugin
 **********************************************************************/

(function($) {

    $.widget('tailbone.gridcore', {

        _create: function() {

            var that = this;

            // Add hover highlight effect to grid rows during mouse-over.
            // this.element.on('mouseenter', 'tbody tr:not(.header)', function() {
            this.element.on('mouseenter', 'tr:not(.header)', function() {
                $(this).addClass('hovering');
            });
            // this.element.on('mouseleave', 'tbody tr:not(.header)', function() {
            this.element.on('mouseleave', 'tr:not(.header)', function() {
                $(this).removeClass('hovering');
            });

            // do some extra stuff for grids with checkboxes

            // mark rows selected on page load, as needed
            this.element.find('tr:not(.header) td.checkbox :checkbox:checked').each(function() {
                $(this).parents('tr:first').addClass('selected');
            });

            // (un-)check all rows when clicking check-all box in header
            if (this.element.find('tr.header td.checkbox :checkbox').length) {
                this.element.on('click', 'tr.header td.checkbox :checkbox', function() {
                    var checked = $(this).prop('checked');
                    var rows = that.element.find('tr:not(.header)');
                    rows.find('td.checkbox :checkbox').prop('checked', checked);
                    if (checked) {
                        rows.addClass('selected');
                    } else {
                        rows.removeClass('selected');
                    }
                    that.element.trigger('gridchecked', that.count_selected());
                });
            }

            // when row with checkbox is clicked, toggle selected status,
            // unless clicking checkbox (since that already toggles it) or a
            // link (since that does something completely different)
            this.element.on('click', 'tr:not(.header)', function(event) {
                var el = $(event.target);
                if (!el.is('a') && !el.is(':checkbox')) {
                    $(this).find('td.checkbox :checkbox').click();
                }
            });

            this.element.on('change', 'tr:not(.header) td.checkbox :checkbox', function() {
                if (this.checked) {
                    $(this).parents('tr:first').addClass('selected');
                } else {
                    $(this).parents('tr:first').removeClass('selected');
                }
                that.element.trigger('gridchecked', that.count_selected());
            });

            // Show 'more' actions when user hovers over 'more' link.
            this.element.on('mouseenter', '.actions a.more', function() {
                that.element.find('.actions div.more').hide();
                $(this).siblings('div.more')
                    .show()
                    .position({my: 'left-5 top-4', at: 'left top', of: $(this)});
            });
            this.element.on('mouseleave', '.actions div.more', function() {
                $(this).hide();
            });

            // Add speed bump for "Delete Row" action, if grid is so configured.
            if (this.element.data('delete-speedbump')) {
                this.element.on('click', 'tr:not(.header) .actions a.delete', function() {
                    return confirm("Are you sure you wish to delete this object?");
                });
            }
        },

        count_selected: function() {
            return this.element.find('tr:not(.header) td.checkbox :checkbox:checked').length;
        },

        // TODO: deprecate / remove this?
        count_checked: function() {
            return this.count_selected();
        },

        selected_rows: function() {
            return this.element.find('tr:not(.header) td.checkbox :checkbox:checked').parents('tr:first');
        },

        all_uuids: function() {
            var uuids = [];
            this.element.find('tr:not(.header)').each(function() {
                uuids.push($(this).data('uuid'));
            });
            return uuids;
        },

        selected_uuids: function() {
            var uuids = [];
            this.element.find('tr:not(.header) td.checkbox :checkbox:checked').each(function() {
                uuids.push($(this).parents('tr:first').data('uuid'));
            });
            return uuids;
        }

    });

})( jQuery );


/**********************************************************************
 * gridwrapper plugin
 **********************************************************************/

(function($) {
    
    $.widget('tailbone.gridwrapper', {

        _create: function() {

            var that = this;

            // Snag some element references.
            this.filters = this.element.find('.newfilters');
            this.filters_form = this.filters.find('form');
            this.add_filter = this.filters.find('#add-filter');
            this.apply_filters = this.filters.find('#apply-filters');
            this.default_filters = this.filters.find('#default-filters');
            this.clear_filters = this.filters.find('#clear-filters');
            this.save_defaults = this.filters.find('#save-defaults');
            this.grid = this.element.find('.grid');

            // add standard grid behavior
            this.grid.gridcore();

            // Enhance filters etc.
            this.filters.find('.filter').gridfilter();
            this.apply_filters.button('option', 'icons', {primary: 'ui-icon-search'});
            this.default_filters.button('option', 'icons', {primary: 'ui-icon-home'});
            this.clear_filters.button('option', 'icons', {primary: 'ui-icon-trash'});
            this.save_defaults.button('option', 'icons', {primary: 'ui-icon-disk'});
            if (! this.filters.find('.active:checked').length) {
                this.apply_filters.button('disable');
            }
            this.add_filter.selectmenu({
                width: '15em',

                // Initially disabled if contains no enabled filter options.
                disabled: this.add_filter.find('option:enabled').length == 1,

                // When add-filter choice is made, show/focus new filter value input,
                // and maybe hide the add-filter selection or show the apply button.
                change: function (event, ui) {
                    var filter = that.filters.find('#filter-' + ui.item.value);
                    var select = $(this);
                    var option = ui.item.element;
                    filter.gridfilter('active', true);
                    filter.gridfilter('focus');
                    select.val('');
                    option.attr('disabled', 'disabled');
                    select.selectmenu('refresh');
                    if (select.find('option:enabled').length == 1) { // prompt is always enabled
                        select.selectmenu('disable');
                    }
                    that.apply_filters.button('enable');
                }
            });

            this.add_filter.on('selectmenuopen', function(event, ui) {
                show_all_options($(this));
            });

            // Intercept filters form submittal, and submit via AJAX instead.
            this.filters_form.on('submit', function() {
                var settings = {filter: true, partial: true};
                if (that.filters_form.find('input[name="save-current-filters-as-defaults"]').val() == 'true') {
                    settings['save-current-filters-as-defaults'] = true;
                }
                that.filters.find('.filter').each(function() {

                    // currently active filters will be included in form data
                    if ($(this).gridfilter('active')) {
                        settings[$(this).data('key')] = $(this).gridfilter('value');
                        settings[$(this).data('key') + '.verb'] = $(this).gridfilter('verb');

                    // others will be hidden from view
                    } else {
                        $(this).gridfilter('hide');
                    }
                });

                // if no filters are visible, disable submit button
                if (! that.filters.find('.filter:visible').length) {
                    that.apply_filters.button('disable');
                }

                // okay, submit filters to server and refresh grid
                that.refresh(settings);
                return false;
            });

            // When user clicks Default Filters button, refresh page with
            // instructions for the server to reset filters to default settings.
            this.default_filters.click(function() {
                that.filters_form.off('submit');
                that.filters_form.find('input[name="reset-to-default-filters"]').val('true');
                that.element.mask("Refreshing data...");
                that.filters_form.get(0).submit();
            });

            // When user clicks Save Defaults button, refresh the grid as with
            // Apply Filters, but add an instruction for the server to save
            // current settings as defaults for the user.
            this.save_defaults.click(function() {
                that.filters_form.find('input[name="save-current-filters-as-defaults"]').val('true');
                that.filters_form.submit();
                that.filters_form.find('input[name="save-current-filters-as-defaults"]').val('false');
            });

            // When user clicks Clear Filters button, deactivate all filters
            // and refresh the grid.
            this.clear_filters.click(function() {
                that.filters.find('.filter').each(function() {
                    if ($(this).gridfilter('active')) {
                        $(this).gridfilter('active', false);
                    }
                });
                that.filters_form.submit();
            });

            // Refresh data when user clicks a sortable column header.
            this.element.on('click', 'tr.header a', function() {
                var td = $(this).parent();
                var data = {
                    sortkey: $(this).data('sortkey'),
                    sortdir: (td.hasClass('asc')) ? 'desc' : 'asc',
                    page: 1,
                    partial: true
                };
                that.refresh(data);
                return false;
            });

            // Refresh data when user chooses a new page size setting.
            this.element.on('change', '.pager #pagesize', function() {
                var settings = {
                    partial: true,
                    pagesize: $(this).val()
                };
                that.refresh(settings);
            });

            // Refresh data when user clicks a pager link.
            this.element.on('click', '.pager a', function() {
                that.refresh(this.search.substring(1)); // remove leading '?'
                return false;
            });
        },

        // Refreshes the visible data within the grid, according to the given settings.
        refresh: function(settings) {
            var that = this;
            this.element.mask("Refreshing data...");
            $.get(this.grid.data('url'), settings, function(data) {
                that.grid.replaceWith(data);
                that.grid = that.element.find('.grid');
                that.grid.gridcore();
                that.element.unmask();
            });
        },

        results_count: function(as_text) {
            var count = null;
            var match = /showing \d+ thru \d+ of (\S+)/.exec(this.element.find('.pager .showing').text());
            if (match) {
                count = match[1];
                if (!as_text) {
                    count = parseInt(count, 10);
                }
            }
            return count;
        },

        all_uuids: function() {
            return this.grid.gridcore('all_uuids');
        },

        selected_uuids: function() {
            return this.grid.gridcore('selected_uuids');
        }

    });
    
})( jQuery );


/**********************************************************************
 * gridfilter plugin
 **********************************************************************/

(function($) {
    
    $.widget('tailbone.gridfilter', {

        _create: function() {

            var that = this;

            // Track down some important elements.
            this.checkbox = this.element.find('input[name$="-active"]');
            this.label = this.element.find('label');
            this.inputs = this.element.find('.inputs');
            this.add_filter = this.element.parents('.grid-wrapper').find('#add-filter');

            // Hide the checkbox and label, and add button for toggling active status.
            this.checkbox.addClass('ui-helper-hidden-accessible');
            this.label.hide();
            this.activebutton = $('<button type="button" class="toggle" />')
                .insertAfter(this.label)
                .text(this.label.text())
                .button({
                    icons: {primary: 'ui-icon-blank'}
                });

            // Enhance verb dropdown as selectmenu.
            this.verb_select = this.inputs.find('.verb');
            this.valueless_verbs = {};
            $.each(this.verb_select.data('hide-value-for').split(' '), function(index, value) {
                that.valueless_verbs[value] = true;
            });
            this.verb_select.selectmenu({
                width: '15em',
                change: function(event, ui) {
                    if (ui.item.value in that.valueless_verbs) {
                        that.inputs.find('.value').hide();
                    } else {
                        that.inputs.find('.value').show();
                        that.focus();
                        that.select();
                    }
                }
            });

            this.verb_select.on('selectmenuopen', function(event, ui) {
                show_all_options($(this));
            });

            // Enhance any date values with datepicker widget.
            this.inputs.find('.value input[data-datepicker="true"]').datepicker({
                dateFormat: 'yy-mm-dd',
                changeYear: true,
                changeMonth: true
            });

            // Enhance any choice/dropdown values with selectmenu.
            this.inputs.find('.value select').selectmenu({
                // provide sane width for value dropdown
                width: '15em'
            });

            this.inputs.find('.value select').on('selectmenuopen', function(event, ui) {
                show_all_options($(this));
            });

            // Listen for button click, to keep checkbox in sync.
            this._on(this.activebutton, {
                click: function(e) {
                    var checked = !this.checkbox.is(':checked');
                    this.checkbox.prop('checked', checked);
                    this.refresh();
                    if (checked) {
                        this.focus();
                    }
                }
            });

            // Update the initial state of the button according to checkbox.
            this.refresh();
        },

        refresh: function() {
            if (this.checkbox.is(':checked')) {
                this.activebutton.button('option', 'icons', {primary: 'ui-icon-check'});
                if (this.verb() in this.valueless_verbs) {
                    this.inputs.find('.value').hide();
                } else {
                    this.inputs.find('.value').show();
                }
                this.inputs.show();
            } else {
                this.activebutton.button('option', 'icons', {primary: 'ui-icon-blank'});
                this.inputs.hide();
            }
        },

        active: function(value) {
            if (value === undefined) {
                return this.checkbox.is(':checked');
            }
            if (value) {
                if (!this.checkbox.is(':checked')) {
                    this.checkbox.prop('checked', true);
                    this.refresh();
                    this.element.show();
                }
            } else if (this.checkbox.is(':checked')) {
                this.checkbox.prop('checked', false);
                this.refresh();
            }
        },

        hide: function() {
            this.active(false);
            this.element.hide();
            var option = this.add_filter.find('option[value="' + this.element.data('key') + '"]');
            option.attr('disabled', false);
            if (this.add_filter.selectmenu('option', 'disabled')) {
                this.add_filter.selectmenu('enable');
            }
            this.add_filter.selectmenu('refresh');
        },

        focus: function() {
            this.inputs.find('.value input').focus();
        },

        select: function() {
            this.inputs.find('.value input').select();
        },

        value: function() {
            return this.inputs.find('.value input, .value select').val();
        },

        verb: function() {
            return this.inputs.find('.verb').val();
        }

    });
    
})( jQuery );
