## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />
<%namespace file="/forms/util.mako" import="render_buefy_field" />

<%def name="title()">Declare Credit for Row #${row.sequence}</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.rows_viewable and master.has_perm('view'):
      <li>${h.link_to("View this {}".format(row_model_title), row_action_url('view', row))}</li>
  % endif
</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    function toggleFields(creditType) {
        if (creditType === undefined) {
            creditType = $('select[name="credit_type"]').val();
        }
        if (creditType == 'expired') {
            $('.field-wrapper.expiration_date').show();
        } else {
            $('.field-wrapper.expiration_date').hide();
        }
    }

    $(function() {

        toggleFields();

        $('select[name="credit_type"]').on('selectmenuchange', function(event, ui) {
            toggleFields(ui.item.value);
        });

    });
  </script>
  % endif
</%def>

<%def name="render_buefy_form()">

  <p class="block">
    Please select the "state" of the product, and enter the
    appropriate quantity.
  </p>

  <p class="block">
    Note that this tool will
    <span class="has-text-weight-bold">deduct</span> from the
    "received" quantity, and
    <span class="has-text-weight-bold">add</span> to the
    corresponding credit quantity.
  </p>

  <p class="block">
    Please see ${h.link_to("Receive Row", url('{}.receive_row'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid))}
    if you need to "receive" instead of "convert" the product.
  </p>

  ${parent.render_buefy_form()}

</%def>

<%def name="buefy_form_body()">

  ${render_buefy_field(dform['credit_type'])}

  ${render_buefy_field(dform['quantity'])}

  ${render_buefy_field(dform['expiration_date'], bfield_kwargs={'v-show': "field_model_credit_type == 'expired'"})}

</%def>

<%def name="render_form()">
  % if use_buefy:

      ${form.render_deform(buttons=capture(self.render_form_buttons), form_body=capture(self.buefy_form_body))|n}

  % else:

    <p style="padding: 1em;">
      Please select the "state" of the product, and enter the appropriate
      quantity.
    </p>

    <p style="padding: 1em;">
      Note that this tool will <strong>deduct</strong> from the "received"
      quantity, and <strong>add</strong> to the corresponding credit quantity.
    </p>

    <p style="padding: 1em;">
      Please see ${h.link_to("Receive Row", url('{}.receive_row'.format(route_prefix), uuid=batch.uuid, row_uuid=row.uuid))}
      if you need to "receive" instead of "convert" the product.
    </p>

    ${parent.render_form()}

  % endif
</%def>


${parent.body()}
