## -*- coding: utf-8; -*-
<%inherit file="/batch/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if master.has_perm('edit_row'):
      ${h.javascript_link(request.static_url('tailbone:static/js/numeric.js'))}
      <script type="text/javascript">

        % if not batch.executed:
        // keep track of which cost value is currently being edited
        var editing_catalog_cost = null;
        var editing_invoice_cost = null;

        function start_editing(td) {
            var value = null;
            var text = td.text().replace(/^\s+|\s+$/g, '');
            if (text) {
                td.data('previous-value', text);
                td.text('');
                value = parseFloat(text.replace('$', ''));
            }
            var input = $('<input type="text" />');
            td.append(input);
            value = value ? value.toString() : '';
            input.val(value).select().focus();
        }

        function start_editing_catalog_cost(td) {
            start_editing(td);
            editing_catalog_cost = td;
        }

        function start_editing_invoice_cost(td) {
            start_editing(td);
            editing_invoice_cost = td;
        }

        function start_editing_next_catalog_cost() {
            var tr = editing_catalog_cost.parents('tr:first');
            var next = tr.next('tr:first');
            if (next.length) {
                start_editing_catalog_cost(next.find('td.catalog_unit_cost'));
            } else {
                editing_catalog_cost = null;
            }
        }

        function start_editing_next_invoice_cost() {
            var tr = editing_invoice_cost.parents('tr:first');
            var next = tr.next('tr:first');
            if (next.length) {
                start_editing_invoice_cost(next.find('td.invoice_unit_cost'));
            } else {
                editing_invoice_cost = null;
            }
        }

        function cancel_edit(td) {
            var input = td.find('input');
            input.blur();
            input.remove();
            var value = td.data('previous-value');
            if (value) {
                td.text(value);
            }
        }

        function cancel_edit_catalog_cost() {
            cancel_edit(editing_catalog_cost);
            editing_catalog_cost = null;
        }

        function cancel_edit_invoice_cost() {
            cancel_edit(editing_invoice_cost);
            editing_invoice_cost = null;
        }

        % endif

        $(function() {

            % if not batch.executed:
            $('.grid-wrapper').on('click', '.grid td.catalog_unit_cost', function() {
                if (editing_catalog_cost) {
                    editing_catalog_cost.find('input').focus();
                    return
                }
                if (editing_invoice_cost) {
                    editing_invoice_cost.find('input').focus();
                    return
                }
                var td = $(this);
                start_editing_catalog_cost(td);
            });

            $('.grid-wrapper').on('click', '.grid td.invoice_unit_cost', function() {
                if (editing_invoice_cost) {
                    editing_invoice_cost.find('input').focus();
                    return
                }
                if (editing_catalog_cost) {
                    editing_catalog_cost.find('input').focus();
                    return
                }
                var td = $(this);
                start_editing_invoice_cost(td);
            });

            $('.grid-wrapper').on('keyup', '.grid td.catalog_unit_cost input', function(event) {
                var input = $(this);

                // let numeric keys modify input value
                if (! key_modifies(event)) {

                    // when user presses Enter while editing cost value, submit
                    // value to server for immediate persistence
                    if (event.which == 13) {
                        $('.grid-wrapper').mask("Updating cost...");
                        var url = '${url('receiving.update_row_cost', uuid=batch.uuid)}';
                        var td = input.parents('td:first');
                        var tr = td.parents('tr:first');
                        var data = {
                            '_csrf': $('[name="_csrf"]').val(),
                            'row_uuid': tr.data('uuid'),
                            'catalog_unit_cost': input.val()
                        };
                        $.post(url, data, function(data) {
                            if (data.error) {
                                alert(data.error);
                            } else {
                                var total = null;

                                // update catalog cost for row
                                td.text(data.row.catalog_unit_cost);

                                // mark cost as confirmed
                                if (data.row.catalog_cost_confirmed) {
                                    tr.addClass('catalog_cost_confirmed');
                                }

                                input.blur();
                                input.remove();
                                start_editing_next_catalog_cost();
                            }
                            $('.grid-wrapper').unmask();
                        });

                    // When user presses Escape while editing totals, cancel the edit.
                    } else if (event.which == 27) {
                        cancel_edit_catalog_cost();

                    // Most other keys at this point should be unwanted...
                    } else if (! key_allowed(event)) {
                        return false;
                    }
                }
            });

            $('.grid-wrapper').on('keyup', '.grid td.invoice_unit_cost input', function(event) {
                var input = $(this);

                // let numeric keys modify input value
                if (! key_modifies(event)) {

                    // when user presses Enter while editing cost value, submit
                    // value to server for immediate persistence
                    if (event.which == 13) {
                        $('.grid-wrapper').mask("Updating cost...");
                        var url = '${url('receiving.update_row_cost', uuid=batch.uuid)}';
                        var td = input.parents('td:first');
                        var tr = td.parents('tr:first');
                        var data = {
                            '_csrf': $('[name="_csrf"]').val(),
                            'row_uuid': tr.data('uuid'),
                            'invoice_unit_cost': input.val()
                        };
                        $.post(url, data, function(data) {
                            if (data.error) {
                                alert(data.error);
                            } else {
                                var total = null;

                                // update unit cost for row
                                td.text(data.row.invoice_unit_cost);

                                // update invoice total for row
                                total = tr.find('td.invoice_total_calculated');
                                total.text('$' + data.row.invoice_total_calculated);

                                // update invoice total for batch
                                total = $('.form .field-wrapper.invoice_total_calculated .field');
                                total.text('$' + data.batch.invoice_total_calculated);

                                // mark cost as confirmed
                                if (data.row.invoice_cost_confirmed) {
                                    tr.addClass('invoice_cost_confirmed');
                                }

                                input.blur();
                                input.remove();
                                start_editing_next_invoice_cost();
                            }
                            $('.grid-wrapper').unmask();
                        });

                    // When user presses Escape while editing totals, cancel the edit.
                    } else if (event.which == 27) {
                        cancel_edit_invoice_cost();

                    // Most other keys at this point should be unwanted...
                    } else if (! key_allowed(event)) {
                        return false;
                    }
                }
            });
            % endif

            $('.grid-wrapper').on('click', '.grid .actions a.transform', function() {

                var form = $('form[name="transform-unit-form"]');
                var row_uuid = $(this).parents('tr:first').data('uuid');
                form.find('[name="row_uuid"]').val(row_uuid);

                $.get(form.attr('action'), {row_uuid: row_uuid}, function(data) {

                    if (typeof(data) == 'object') {
                        alert(data.error);

                    } else {
                        $('#transform-unit-dialog').html(data);
                        $('#transform-unit-dialog').dialog({
                            title: "Transform Pack to Unit Item",
                            width: 800,
                            height: 450,
                            modal: true,
                            buttons: [
                                {
                                    text: "Transform",
                                    click: function(event) {
                                        disable_button(dialog_button(event));
                                        form.submit();
                                    }
                                },
                                {
                                    text: "Cancel",
                                    click: function() {
                                        $(this).dialog('close');
                                    }
                                }
                            ]
                        });
                    }
                });

                return false;
            });

        });

      </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if not batch.executed and master.has_perm('edit_row'):
      <style type="text/css">
        .grid tr:not(.header) td.catalog_unit_cost,
        .grid tr:not(.header) td.invoice_unit_cost {
          cursor: pointer;
          background-color: #fcc;
        }
        .grid tr.catalog_cost_confirmed:not(.header) td.catalog_unit_cost,
        .grid tr.invoice_cost_confirmed:not(.header) td.invoice_unit_cost {
          background-color: #cfc;
        }
        .grid td.catalog_unit_cost input,
        .grid td.invoice_unit_cost input {
          width: 4rem;
        }
      </style>
  % endif
</%def>

<%def name="render_po_vs_invoice_helper()">
  % if use_buefy and master.handler.has_purchase_order(batch) and master.handler.has_invoice_file(batch):
      <div class="object-helper">
        <h3>PO vs. Invoice</h3>
        <div class="object-helper-content">
          ${po_vs_invoice_breakdown_grid}
        </div>
      </div>
  % endif
</%def>

<%def name="render_auto_receive_helper()">
  % if master.has_perm('auto_receive') and master.can_auto_receive(batch):

      <div class="object-helper">
        <h3>Tools</h3>
        <div class="object-helper-content">
          % if use_buefy:
              <b-button type="is-primary"
                        @click="autoReceiveShowDialog = true"
                        icon-pack="fas"
                        icon-left="check">
                Auto-Receive All Items
              </b-button>
          % else:
              ${h.form(url('{}.auto_receive'.format(route_prefix), uuid=batch.uuid), class_='autodisable')}
              ${h.csrf_token(request)}
              ${h.submit('submit', "Auto-Receive All Items")}
              ${h.end_form()}
          % endif
        </div>
      </div>

      % if use_buefy:
          <b-modal has-modal-card
                   :active.sync="autoReceiveShowDialog">
            <div class="modal-card">

              <header class="modal-card-head">
                <p class="modal-card-title">Auto-Receive All Items</p>
              </header>

              <section class="modal-card-body">
                <p class="block">
                  You can automatically set the "received" quantity to
                  match the "shipped" quantity for all items, based on
                  the invoice.
                </p>
                <p class="block">
                  Would you like to do so?
                </p>
              </section>

              <footer class="modal-card-foot">
                <b-button @click="autoReceiveShowDialog = false">
                  Cancel
                </b-button>
                ${h.form(url('{}.auto_receive'.format(route_prefix), uuid=batch.uuid), **{'@submit': 'autoReceiveSubmitting = true'})}
                ${h.csrf_token(request)}
                <b-button type="is-primary"
                          native-type="submit"
                          :disabled="autoReceiveSubmitting"
                          icon-pack="fas"
                          icon-left="check">
                  {{ autoReceiveSubmitting ? "Working, please wait..." : "Auto-Receive All Items" }}
                </b-button>
                ${h.end_form()}
              </footer>
            </div>
          </b-modal>
      % endif
  % endif
</%def>

<%def name="object_helpers()">
  ${self.render_status_breakdown()}
  ${self.render_po_vs_invoice_helper()}
  ${self.render_execute_helper()}
  ${self.render_auto_receive_helper()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.autoReceiveShowDialog = false
    ThisPageData.autoReceiveSubmitting = false

    % if po_vs_invoice_breakdown_data is not Undefined:
        ThisPageData.poVsInvoiceBreakdownData = ${json.dumps(po_vs_invoice_breakdown_data)|n}

        ThisPage.methods.autoFilterPoVsInvoice = function(row) {
            let filters = []
            if (row.key == 'both') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_not_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_not_null'},
                ]
            } else if (row.key == 'po_not_invoice') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_not_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_null'},
                ]
            } else if (row.key == 'invoice_not_po') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_not_null'},
                ]
            } else if (row.key == 'neither') {
                filters = [
                    {key: 'po_line_number',
                     verb: 'is_null'},
                    {key: 'invoice_line_number',
                     verb: 'is_null'},
                ]
            }

            if (!filters.length) {
                return
            }

            this.$refs.rowGrid.setFilters(filters)
            document.getElementById('rowGrid').scrollIntoView({
                behavior: 'smooth',
            })
        }

    % endif

  </script>
</%def>


${parent.body()}

% if master.handler.allow_truck_dump_receiving() and master.has_perm('edit_row'):
    ${h.form(url('{}.transform_unit_row'.format(route_prefix), uuid=batch.uuid), name='transform-unit-form')}
    ${h.csrf_token(request)}
    ${h.hidden('row_uuid')}
    ${h.end_form()}

    <div id="transform-unit-dialog" style="display: none;">
      <p>hello world</p>
    </div>
% endif
