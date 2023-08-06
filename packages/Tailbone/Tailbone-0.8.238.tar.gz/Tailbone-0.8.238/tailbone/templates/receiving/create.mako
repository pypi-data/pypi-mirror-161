## -*- coding: utf-8; -*-
<%inherit file="/batch/create.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  ${self.func_show_batch_type()}
  <script type="text/javascript">

    % if master.handler.allow_truck_dump_receiving():
    var batch_vendor_map = ${json.dumps(batch_vendor_map)|n};
    % endif

    $(function() {

        $('.batch_type select').on('selectmenuchange', function(event, ui) {
            show_batch_type(ui.item.value);
        });

        $('.truck_dump_batch_uuid select').on('selectmenuchange', function(event, ui) {
            var form = $(this).parents('form');
            var uuid = ui.item.value ? batch_vendor_map[ui.item.value] : '';
            form.find('input[name="vendor_uuid"]').val(uuid);
        });

        show_batch_type();
    });

  </script>
  % endif
</%def>

<%def name="func_show_batch_type()">
  <script type="text/javascript">

    function show_batch_type(batch_type) {

        if (batch_type === undefined) {
            batch_type = $('.field-wrapper.batch_type select').val();
        }

        if (batch_type == 'from_scratch') {
            $('.field-wrapper.truck_dump_batch_uuid').hide();
            $('.field-wrapper.invoice_file').hide();
            $('.field-wrapper.invoice_parser_key').hide();
            $('.field-wrapper.vendor_uuid').show();
            $('.field-wrapper.date_ordered').show();
            $('.field-wrapper.date_received').show();
            $('.field-wrapper.po_number').show();
            $('.field-wrapper.invoice_date').show();
            $('.field-wrapper.invoice_number').show();

        } else if (batch_type == 'truck_dump_children_first') {
            $('.field-wrapper.truck_dump_batch_uuid').hide();
            $('.field-wrapper.invoice_file').hide();
            $('.field-wrapper.invoice_parser_key').hide();
            $('.field-wrapper.vendor_uuid').show();
            $('.field-wrapper.date_ordered').hide();
            $('.field-wrapper.date_received').show();
            $('.field-wrapper.po_number').hide();
            $('.field-wrapper.invoice_date').hide();
            $('.field-wrapper.invoice_number').hide();

        } else if (batch_type == 'truck_dump_children_last') {
            $('.field-wrapper.truck_dump_batch_uuid').hide();
            $('.field-wrapper.invoice_file').hide();
            $('.field-wrapper.invoice_parser_key').hide();
            $('.field-wrapper.vendor_uuid').show();
            $('.field-wrapper.date_ordered').hide();
            $('.field-wrapper.date_received').show();
            $('.field-wrapper.po_number').hide();
            $('.field-wrapper.invoice_date').hide();
            $('.field-wrapper.invoice_number').hide();
        }
    }

  </script>
</%def>

${parent.body()}
