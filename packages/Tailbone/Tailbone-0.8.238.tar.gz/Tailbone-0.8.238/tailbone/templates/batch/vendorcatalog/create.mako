## -*- coding: utf-8; -*-
<%inherit file="/batch/create.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    var vendormap = {
        % for i, parser in enumerate(parsers, 1):
            '${parser.key}': ${parser.vendormap_value|n}${',' if i < len(parsers) else ''}
        % endfor
    };

    $(function() {

        if ($('select[name="parser_key"] option:first').is(':selected')) {
            $('.vendor_uuid .autocomplete-container').hide();
        } else {
            $('.vendor_uuid input[name="vendor_uuid"]').val('');
            $('.vendor_uuid .autocomplete-display').hide();
            $('.vendor_uuid .autocomplete-display button').show();
            $('.vendor_uuid .autocomplete-textbox').val('');
            $('.vendor_uuid .autocomplete-textbox').show();
            $('.vendor_uuid .autocomplete-container').show();
        }

        $('select[name="parser_key"]').on('selectmenuchange', function() {
            if ($(this).find('option:first').is(':selected')) {
                $('.vendor_uuid .autocomplete-container').hide();
            } else {
                var vendor = vendormap[$(this).val()];
                if (vendor) {
                    $('.vendor_uuid input[name="vendor_uuid"]').val(vendor.uuid);
                    $('.vendor_uuid .autocomplete-textbox').hide();
                    $('.vendor_uuid .autocomplete-display span:first').text(vendor.name);
                    $('.vendor_uuid .autocomplete-display button').hide();
                    $('.vendor_uuid .autocomplete-display').show();
                    $('.vendor_uuid .autocomplete-container').show();
                } else {
                    $('.vendor_uuid input[name="vendor_uuid"]').val('');
                    $('.vendor_uuid .autocomplete-display').hide();
                    $('.vendor_uuid .autocomplete-display button').show();
                    $('.vendor_uuid .autocomplete-textbox').val('');
                    $('.vendor_uuid .autocomplete-textbox').show();
                    $('.vendor_uuid .autocomplete-container').show();
                    $('.vendor_uuid .autocomplete-textbox').focus();
                }
            }
        });

    });
  </script>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ${form.component_studly}Data.parsers = ${json.dumps(parsers_data)|n}

    ${form.component_studly}Data.vendorName = null
    ${form.component_studly}Data.vendorNameReplacement = null

    ${form.component_studly}.watch.field_model_parser_key = function(val) {
        let parser = this.parsers[val]
        if (parser.vendor_uuid) {
            if (this.field_model_vendor_uuid != parser.vendor_uuid) {
                // this.field_model_vendor_uuid = parser.vendor_uuid
                // this.vendorName = parser.vendor_name
                this.$refs.vendorAutocomplete.setSelection({
                    value: parser.vendor_uuid,
                    label: parser.vendor_name,
                })
            }
        }
    }

    ${form.component_studly}.methods.vendorLabelChanging = function(label) {
        this.vendorNameReplacement = label
    }

    ${form.component_studly}.methods.vendorChanged = function(uuid) {
        if (uuid) {
            this.vendorName = this.vendorNameReplacement
            this.vendorNameReplacement = null
        }
    }

  </script>
</%def>


${parent.body()}
