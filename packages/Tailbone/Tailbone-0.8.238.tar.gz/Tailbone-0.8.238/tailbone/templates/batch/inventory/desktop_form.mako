## -*- coding: utf-8; -*-
<%inherit file="/base.mako" />

<%def name="title()">Inventory Form</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  ${h.javascript_link(request.static_url('tailbone:static/js/numeric.js'))}
  <script type="text/javascript">

    function assert_quantity() {
        % if allow_cases:
        var cases = parseFloat($('#cases').val());
        if (!isNaN(cases)) {
            if (cases > 999999) {
                alert("Case amount is invalid!");
                $('#cases').select().focus();
                return false;
            }
            return true;
        }
        % endif
        var units = parseFloat($('#units').val());
        if (!isNaN(units)) {
            if (units > 999999) {
                alert("Unit amount is invalid!");
                $('#units').select().focus();
                return false;
            }
            return true;
        }
        alert("Please provide case and/or unit quantity");
        % if allow_cases:
        $('#cases').select().focus();
        % else:
        $('#units').select().focus();
        % endif
        return false;
    }

    function invalid_product(msg) {
        $('#product-info p').text(msg);
        $('#product-info img').hide();
        $('#upc').focus().select();
        % if allow_cases:
        $('.field-wrapper.cases input').prop('disabled', true);
        % endif
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
                $('#product-info p').html("please ENTER a scancode");
                $('#product-info img').hide();
                $('#product-info .warning').hide();
                $('.product-fields').hide();
                // $('.receiving-fields').hide();
                % if allow_cases:
                $('.field-wrapper.cases input').prop('disabled', true);
                % endif
                $('.field-wrapper.units input').prop('disabled', true);
                $('.buttons button').button('disable');
                return true;
            }

            // when user presses ENTER, do product lookup
            if (event.which == 13) {
                var upc = $(this).val();
                var data = {'upc': upc};
                $.get('${url('batch.inventory.desktop_lookup', uuid=batch.uuid)}', data, function(data) {

                    if (data.error) {
                        alert(data.error);
                        if (data.redirect) {
                            $('#inventory-form').mask("Redirecting...");
                            location.href = data.redirect;
                        }

                    } else if (data.product) {
                        $('#upc').val(data.product.upc_pretty);
                        $('#product').val(data.product.uuid);
                        $('#brand_name').val(data.product.brand_name);
                        $('#description').val(data.product.description);
                        $('#size').val(data.product.size);
                        $('#case_quantity').val(data.product.case_quantity);

                        if (data.force_unit_item) {
                            $('#product-info .warning.force-unit').show();
                        }

                        if (data.already_present_in_batch) {
                            $('#product-info .warning.present').show();
                            $('#cases').val(data.cases);
                            $('#units').val(data.units);

                        } else if (data.product.type2) {
                            $('#units').val(data.product.units);
                        }

                        $('#product-info p').text(data.product.full_description);
                        $('#product-info img').attr('src', data.product.image_url).show();
                        if (! data.product.uuid) {
                            // $('#product-info .warning.notfound').show();
                            $('.product-fields').show();
                        }
                        $('#product-info .warning.notordered').show();
                        % if allow_cases:
                        $('.field-wrapper.cases input').prop('disabled', false);
                        % endif
                        $('.field-wrapper.units input').prop('disabled', false);
                        $('.buttons button').button('enable');

                        if (data.product.type2) {
                            $('#units').focus().select();
                        } else {
                            % if allow_cases and prefer_cases:
                            if ($('#cases').val()) {
                                $('#cases').focus().select();
                            } else if ($('#units').val()) {
                                $('#units').focus().select();
                            } else {
                                $('#cases').focus().select();
                            }
                            % else:
                            $('#units').focus().select();
                            % endif
                        }

                    // TODO: this is maybe useful if "new products" may be added via inventory batch
                    // } else if (data.upc) {
                    //     $('#upc').val(data.upc_pretty);
                    //     $('#product-info p').text("product not found in our system");
                    //     $('#product-info img').attr('src', data.image_url).show();

                    //     $('#product').val('');
                    //     $('#brand_name').val('');
                    //     $('#description').val('');
                    //     $('#size').val('');
                    //     $('#case_quantity').val('');

                    //     $('#product-info .warning.notfound').show();
                    //     $('.product-fields').show();
                    //     $('#brand_name').focus();
                    //     $('.field-wrapper.cases input').prop('disabled', false);
                    //     $('.field-wrapper.units input').prop('disabled', false);
                    //     $('.buttons button').button('enable');

                    } else {
                        invalid_product('product not found');
                    }
                });
            }
            return false;
        });

        $('#inventory-form').submit(function() {
            if (! assert_quantity()) {
                return false;
            }
            disable_submit_button(this);
            $(this).mask("Working...");
        });

        $('#upc').focus();
        % if allow_cases:
        $('.field-wrapper.cases input').prop('disabled', true);
        % endif
        $('.field-wrapper.units input').prop('disabled', true);
        $('.buttons button').button('disable');

    });
  </script>
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    #product-info {
        margin-top: 0.5em;
        text-align: center;
    }

    #product-info p {
        margin-left: 0.5em;
    }

    #product-info .img-wrapper {
        height: 150px;
        margin: 0.5em 0;
    }

    #product-info .warning {
        background: #f66;
        display: none;
    }

  </style>
</%def>


<%def name="context_menu_items()">
  <li>${h.link_to("Back to Inventory Batch", url('batch.inventory.view', uuid=batch.uuid))}</li>
</%def>


<ul id="context-menu">
  ${self.context_menu_items()}
</ul>

<div class="form-wrapper">
  ${h.form(form.action_url, id='inventory-form')}
  ${h.csrf_token(request)}

  <div class="field-wrapper">
    <label for="upc">Product UPC</label>
    <div class="field">
      ${h.hidden('product')}
      <div>${h.text('upc', autocomplete='off')}</div>
      <div id="product-info">
        <p>please ENTER a scancode</p>
        <div class="img-wrapper"><img /></div>
        <div class="warning notfound">please confirm UPC and provide more details</div>
        <div class="warning present">product already exists in batch, please confirm count</div>
        <div class="warning force-unit">pack item scanned, but must count units instead</div>
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

  % if allow_cases:
      <div class="field-wrapper cases">
        <label for="cases">Cases</label>
        <div class="field">${h.text('cases', autocomplete='off')}</div>
      </div>
  % endif

  <div class="field-wrapper units">
    <label for="units">Units</label>
    <div class="field">${h.text('units', autocomplete='off')}</div>
  </div>

  <div class="buttons">
    ${h.submit('submit', "Submit")}
  </div>

  ${h.end_form()}
</div>
