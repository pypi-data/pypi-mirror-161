## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if not use_buefy:
  <style type="text/css">

    table.label-printing th {
        font-weight: normal;
        padding: 0px 0px 2px 4px;
        text-align: left;
    }

    table.label-printing td {
        padding: 0px 0px 0px 4px;
    }

    table.label-printing #label-quantity {
        text-align: right;
        width: 30px;
    }

    div.grid table tbody td.size,
    div.grid table tbody td.regular_price_uuid,
    div.grid table tbody td.current_price_uuid {
        padding-right: 6px;
        text-align: right;
    }
    
    div.grid table tbody td.labels {
        text-align: center;
    }
    
  </style>
  % endif
</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy and label_profiles and master.has_perm('print_labels'):
      <script type="text/javascript">

      $(function() {

          $('.grid-wrapper .grid-header .tools select').selectmenu();

          $('.grid-wrapper').on('click', 'a.print_label', function() {
              var tr = $(this).parents('tr:first');
              var quantity = $('table.label-printing #label-quantity');
              if (isNaN(quantity.val())) {
                  alert("You must provide a valid label quantity.");
                  quantity.select();
                  quantity.focus();
              } else {
                  quantity = quantity.val();

                  var threshold = ${json.dumps(quick_label_speedbump_threshold)|n};
                  if (threshold && parseInt(quantity) >= threshold) {
                      if (!confirm("Are you sure you want to print " + quantity + " labels?")) {
                          return false;
                      }
                  }

                  var data = {
                      product: tr.data('uuid'),
                      profile: $('#label-profile').val(),
                      quantity: quantity
                  };
                  $.get('${url('products.print_labels')}', data, function(data) {
                      if (data.error) {
                          alert("An error occurred while attempting to print:\n\n" + data.error);
                      } else if (quantity == '1') {
                          alert("1 label has been printed.");
                      } else {
                          alert(quantity + " labels have been printed.");
                      }
                  });
              }
              return false;
          });
      });

      </script>
  % endif
</%def>

<%def name="grid_tools()">
  ${parent.grid_tools()}
  % if label_profiles and master.has_perm('print_labels'):
      % if use_buefy:
          <b-field grouped>
            <b-field label="Label">
              <b-select v-model="quickLabelProfile">
                % for profile in label_profiles:
                    <option value="${profile.uuid}">
                      ${profile.description}
                    </option>
                % endfor
              </b-select>
            </b-field>
            <b-field label="Qty.">
              <b-input v-model="quickLabelQuantity"
                       ref="quickLabelQuantityInput"
                       style="width: 4rem;">
              </b-input>
            </b-field>
          </b-field>
      % else:
      <table class="label-printing">
        <thead>
          <tr>
            <th>Label</th>
            <th>Qty.</th>
          </tr>
        </thead>
        <tbody>
          <td>
            <select name="label-profile" id="label-profile">
              % for profile in label_profiles:
                  <option value="${profile.uuid}">${profile.description}</option>
              % endfor
            </select>
          </td>
          <td>
            <input type="text" name="label-quantity" id="label-quantity" value="1" />
          </td>
        </tbody>
      </table>
      % endif
  % endif
</%def>

<%def name="render_grid_component()">
  <${grid.component} :csrftoken="csrftoken"
     % if master.deletable and master.has_perm('delete') and master.delete_confirm == 'simple':
     @deleteActionClicked="deleteObject"
     % endif
     % if label_profiles and master.has_perm('print_labels'):
     @quick-label-print="quickLabelPrint"
     % endif
     >
  </${grid.component}>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if label_profiles and master.has_perm('print_labels'):
      <script type="text/javascript">

        ${grid.component_studly}Data.quickLabelProfile = ${json.dumps(label_profiles[0].uuid)|n}
        ${grid.component_studly}Data.quickLabelQuantity = 1
        ${grid.component_studly}Data.quickLabelSpeedbumpThreshold = ${json.dumps(quick_label_speedbump_threshold)|n}

        ${grid.component_studly}.methods.quickLabelPrint = function(row) {

            let quantity = parseInt(this.quickLabelQuantity)
            if (isNaN(quantity)) {
                alert("You must provide a valid label quantity.")
                this.$refs.quickLabelQuantityInput.focus()
                return
            }

            if (this.quickLabelSpeedbumpThreshold && quantity >= this.quickLabelSpeedbumpThreshold) {
                if (!confirm("Are you sure you want to print " + quantity + " labels?")) {
                    return
                }
            }

            this.$emit('quick-label-print', row.uuid, this.quickLabelProfile, quantity)
        }

        ThisPage.methods.quickLabelPrint = function(product, profile, quantity) {
            let url = '${url('products.print_labels')}'

            let data = new FormData()
            data.append('product', product)
            data.append('profile', profile)
            data.append('quantity', quantity)

            this.submitForm(url, data, response => {
                if (quantity == 1) {
                    alert("1 label has been printed.")
                } else {
                    alert(quantity.toString() + " labels have been printed.")
                }
            })
        }

      </script>
  % endif
</%def>


${parent.body()}
