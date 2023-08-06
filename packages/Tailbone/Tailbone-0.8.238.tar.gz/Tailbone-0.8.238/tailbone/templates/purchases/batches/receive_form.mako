## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">Receiving Form (${batch.vendor})</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.javascript_link(request.static_url('tailbone:static/js/numeric.js'))}
  <script type="text/javascript">

    function assert_quantity() {
        if ($('#cases').val() && parseFloat($('#cases').val())) {
            return true;
        }
        if ($('#units').val() && parseFloat($('#units').val())) {
            return true;
        }
        alert("Please provide case and/or unit quantity");
        $('#cases').select().focus();
        return false;
    }

    function invalid_product(msg) {
        $('#received-product-info p').text(msg);
        $('#received-product-info img').hide();
        $('#upc').focus().select();
        $('.field-wrapper.cases input').prop('disabled', true);
        $('.field-wrapper.units input').prop('disabled', true);
        $('.buttons button').button('disable');
    }

    function pretty_quantity(cases, units) {
        if (cases && units) {
            return cases + " cases, " + units + " units";
        } else if (cases) {
            return cases + " cases";
        } else if (units) {
            return units + " units";
        }
        return '';
    }

    function show_quantity(name, cases, units) {
        var quantity = pretty_quantity(cases, units);
        var field = $('.field-wrapper.quantity_' + name);
        field.find('.field').text(quantity);
        if (quantity || name == 'ordered') {
            field.show();
        } else {
            field.hide();
        }
    }

    $(function() {

        $('#upc').keydown(function(event) {

            if (key_allowed(event)) {
                return true;
            }
            if (key_modifies(event)) {
                $('#product').val('');
                $('#received-product-info p').html("please ENTER a scancode");
                $('#received-product-info img').hide();
                $('#received-product-info .warning').hide();
                $('.product-fields').hide();
                $('.receiving-fields').hide();
                $('.field-wrapper.cases input').prop('disabled', true);
                $('.field-wrapper.units input').prop('disabled', true);
                $('.buttons button').button('disable');
                return true;
            }

            // when user presses ENTER, do product lookup
            if (event.which == 13) {
                var upc = $(this).val();
                var data = {'upc': upc};
                $.get('${url('purchases.batch.receiving_lookup', uuid=batch.uuid)}', data, function(data) {

                    if (data.error) {
                        alert(data.error);
                        if (data.redirect) {
                            $('#receiving-form').mask("Redirecting...");
                            location.href = data.redirect;
                        }

                    } else if (data.product) {
                        $('#upc').val(data.product.upc_pretty);
                        $('#product').val(data.product.uuid);
                        $('#brand_name').val(data.product.brand_name);
                        $('#description').val(data.product.description);
                        $('#size').val(data.product.size);
                        $('#case_quantity').val(data.product.case_quantity);

                        $('#received-product-info p').text(data.product.full_description);
                        $('#received-product-info img').attr('src', data.product.image_url).show();
                        if (! data.product.uuid) {
                            // $('#received-product-info .warning.notfound').show();
                            $('.product-fields').show();
                        }
                        if (data.product.found_in_batch) {
                            show_quantity('ordered', data.product.cases_ordered, data.product.units_ordered);
                            show_quantity('received', data.product.cases_received, data.product.units_received);
                            show_quantity('damaged', data.product.cases_damaged, data.product.units_damaged);
                            show_quantity('expired', data.product.cases_expired, data.product.units_expired);
                            show_quantity('mispick', data.product.cases_mispick, data.product.units_mispick);
                            $('.receiving-fields').show();
                        } else {
                            $('#received-product-info .warning.notordered').show();
                        }
                        $('.field-wrapper.cases input').prop('disabled', false);
                        $('.field-wrapper.units input').prop('disabled', false);
                        $('.buttons button').button('enable');
                        $('#cases').focus().select();

                    } else if (data.upc) {
                        $('#upc').val(data.upc_pretty);
                        $('#received-product-info p').text("product not found in our system");
                        $('#received-product-info img').attr('src', data.image_url).show();

                        $('#product').val('');
                        $('#brand_name').val('');
                        $('#description').val('');
                        $('#size').val('');
                        $('#case_quantity').val('');

                        $('#received-product-info .warning.notfound').show();
                        $('.product-fields').show();
                        $('#brand_name').focus();
                        $('.field-wrapper.cases input').prop('disabled', false);
                        $('.field-wrapper.units input').prop('disabled', false);
                        $('.buttons button').button('enable');

                    } else {
                        invalid_product('product not found');
                    }
                });
            }
            return false;
        });

        $('#received').click(function() {
            if (! assert_quantity()) {
                return;
            }
            $(this).button('disable').button('option', 'label', "Working...");
            $('#mode').val('received');
            $('#receiving-form').submit();
        });

        $('#damaged').click(function() {
            if (! assert_quantity()) {
                return;
            }
            $(this).button('disable').button('option', 'label', "Working...");
            $('#mode').val('damaged');
            $('#damaged-dialog').dialog({
                title: "Damaged Product",
                modal: true,
                width: '500px',
                buttons: [
                    {
                        text: "OK",
                        click: function() {
                            $('#damaged-dialog').dialog('close');
                            $('#receiving-form #trash').val($('#damaged-dialog #trash').is(':checked') ? '1' : '');
                            $('#receiving-form').submit();
                        }
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            $('#damaged').button('option', 'label', "Damaged").button('enable');
                            $('#damaged-dialog').dialog('close');
                        }
                    }
                ]
            });
        });

        $('#expiration input[type="date"]').datepicker();

        $('#expired').click(function() {
            if (! assert_quantity()) {
                return;
            }
            $(this).button('disable').button('option', 'label', "Working...");
            $('#mode').val('expired');
            $('#expiration').dialog({
                title: "Expired / Short Date",
                modal: true,
                width: '500px',
                buttons: [
                    {
                        text: "OK",
                        click: function() {
                            $('#expiration').dialog('close');
                            $('#receiving-form #expiration_date').val(
                                $('#expiration input[type="date"]').val());
                            $('#receiving-form #trash').val($('#expiration #trash').is(':checked') ? '1' : '');
                            $('#receiving-form').submit();
                        }
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            $('#expired').button('option', 'label', "Expired").button('enable');
                            $('#expiration').dialog('close');
                        }
                    }
                ]
            });
        });

        $('#mispick').click(function() {
            if (! assert_quantity()) {
                return;
            }
            $(this).button('disable').button('option', 'label', "Working...");
            $('#ordered-product').val('');
            $('#ordered-product-textbox').val('');
            $('#ordered-product-info p').html("please ENTER a scancode");
            $('#ordered-product-info img').hide();
            $('#mispick-dialog').dialog({
                title: "Mispick - Ordered Product",
                modal: true,
                width: 400,
                buttons: [
                    {
                        text: "OK",
                        click: function() {
                            if ($('#ordered-product-info .warning').is(':visible')) {
                                alert("You must choose a product which was ordered.");
                                $('#ordered-product-textbox').select().focus();
                                return;
                            }
                            $('#mispick-dialog').dialog('close');
                            $('#mode').val('mispick');
                            $('#receiving-form').submit();
                        }
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            $('#mispick').button('option', 'label', "Mispick").button('enable');
                            $('#mispick-dialog').dialog('close');
                        }
                    }
                ]
            });
        });

        $('#ordered-product-textbox').keydown(function(event) {

            if (key_allowed(event)) {
                return true;
            }
            if (key_modifies(event)) {
                $('#ordered_product').val('');
                $('#ordered-product-info p').html("please ENTER a scancode");
                $('#ordered-product-info img').hide();
                $('#ordered-product-info .warning').hide();
                return true;
            }
            if (event.which == 13) {
                var input = $(this);
                var data = {upc: input.val()};
                $.get('${url('purchases.batch.receiving_lookup', uuid=batch.uuid)}', data, function(data) {
                    if (data.error) {
                        alert(data.error);
                        if (data.redirect) {
                            $('#mispick-dialog').mask("Redirecting...");
                            location.href = data.redirect;
                        }
                    } else if (data.product) {
                        input.val(data.product.upc_pretty);
                        $('#ordered_product').val(data.product.uuid);
                        $('#ordered-product-info p').text(data.product.full_description);
                        $('#ordered-product-info img').attr('src', data.product.image_url).show();
                        if (data.product.found_in_batch) {
                            $('#ordered-product-info .warning').hide();
                        } else {
                            $('#ordered-product-info .warning').show();
                        }
                    } else {
                        $('#ordered-product-info p').text("product not found");
                        $('#ordered-product-info img').hide();
                        $('#ordered-product-info .warning').hide();
                    }
                });
            }
            return false;
        });

        $('#receiving-form').submit(function() {
            $(this).mask("Working...");
        });

        $('#upc').focus();
        $('.field-wrapper.cases input').prop('disabled', true);
        $('.field-wrapper.units input').prop('disabled', true);
        $('.buttons button').button('disable');

    });
  </script>
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .product-info {
        margin-top: 0.5em;
        text-align: center;
    }

    .product-info p {
        margin-left: 0.5em;
    }

    .product-info .img-wrapper {
        height: 150px;
        margin: 0.5em 0;
    }

    #received-product-info .warning {
        background: #f66;
        display: none;
    }

    #mispick-dialog input[type="text"],
    #ordered-product-info {
        width: 320px;
    }

    #ordered-product-info .warning {
        background: #f66;
        display: none;
    }

  </style>
</%def>


<%def name="context_menu_items()">
  <li>${h.link_to("Back to Purchase Batch", url('purchases.batch.view', uuid=batch.uuid))}</li>
</%def>


<ul id="context-menu">
  ${self.context_menu_items()}
</ul>

<div class="form-wrapper">
  ${form.begin(id='receiving-form')}
  ${form.csrf_token()}
  ${h.hidden('mode')}
  ${h.hidden('expiration_date')}
  ${h.hidden('trash')}
  ${h.hidden('ordered_product')}

  <div class="field-wrapper">
    <label for="upc">Receiving UPC</label>
    <div class="field">
      ${h.hidden('product')}
      <div>${h.text('upc', autocomplete='off')}</div>
      <div id="received-product-info" class="product-info">
        <p>please ENTER a scancode</p>
        <div class="img-wrapper"><img /></div>
        <div class="warning notfound">please confirm UPC and provide more details</div>
        <div class="warning notordered">warning: product not found on current purchase</div>
      </div>
    </div>
  </div>

  <div class="product-fields" style="display: none;">

    <div class="field-wrapper brand_name">
      <label for="brand_name">Brand Name</label>
      <div class="field">${h.text('brand_name')}</div>
    </div>

    <div class="field-wrapper description">
      <label for="description">Description</label>
      <div class="field">${h.text('description')}</div>
    </div>

    <div class="field-wrapper size">
      <label for="size">Size</label>
      <div class="field">${h.text('size')}</div>
    </div>

    <div class="field-wrapper case_quantity">
      <label for="case_quantity">Units in Case</label>
      <div class="field">${h.text('case_quantity')}</div>
    </div>

  </div>

  <div class="receiving-fields" style="display: none;">

    <div class="field-wrapper quantity_ordered">
      <label for="quantity_ordered">Ordered</label>
      <div class="field"></div>
    </div>

    <div class="field-wrapper quantity_received">
      <label for="quantity_received">Received</label>
      <div class="field"></div>
    </div>

    <div class="field-wrapper quantity_damaged">
      <label for="quantity_damaged">Damaged</label>
      <div class="field"></div>
    </div>

    <div class="field-wrapper quantity_expired">
      <label for="quantity_expired">Expired</label>
      <div class="field"></div>
    </div>

    <div class="field-wrapper quantity_mispick">
      <label for="quantity_mispick">Mispick</label>
      <div class="field"></div>
    </div>

  </div>

  <div class="field-wrapper cases">
    <label for="cases">Cases</label>
    <div class="field">${h.text('cases', autocomplete='off')}</div>
  </div>

  <div class="field-wrapper units">
    <label for="units">Units</label>
    <div class="field">${h.text('units', autocomplete='off')}</div>
  </div>

  <div class="buttons">
    <button type="button" id="received">Received</button>
    <button type="button" id="damaged">Damaged</button>
    <button type="button" id="expired">Expired</button>
    <!-- <button type="button" id="mispick">Mispick</button> -->
  </div>

  ${form.end()}
</div>

<div id="damaged-dialog" style="display: none;">
  <div class="field-wrapper trash">${h.checkbox('trash', label="Product will be discarded and cannot be returned", checked=False)}</div>
</div>

<div id="expiration" style="display: none;">
  <div class="field-wrapper expiration-date">
    <label for="expiration-date">Expiration Date</label>
    <div class="field">${h.text('expiration-date', type='date')}</div>
  </div>
  <div class="field-wrapper trash">${h.checkbox('trash', label="Product will be discarded and cannot be returned", checked=False)}</div>
</div>

<div id="mispick-dialog" style="display: none;">
  <div>${h.text('ordered-product-textbox', autocomplete='off')}</div>
  <div id="ordered-product-info" class="product-info">
    <p>please ENTER a scancode</p>
    <div class="img-wrapper"><img /></div>
    <div class="warning">warning: product not found on current purchase</div>
  </div>
</div>
