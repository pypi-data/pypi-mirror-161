## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy and request.rattail_config.versioning_enabled() and master.has_perm('versions'):
      <script type="text/javascript">

        function showPriceHistory(typ) {
            var dialog = $('#' + typ + '-price-history-dialog');
            dialog.dialog({
                title: typ[0].toUpperCase() + typ.slice(1) + " Price History",
                width: 600,
                height: 300,
                modal: true,
                buttons: [
                    {
                        text: "Close",
                        click: function() {
                            dialog.dialog('close');
                        }
                    }
                ]
            });
        }

        function showCostHistory() {
            var dialog = $('#cost-history-dialog');
            dialog.dialog({
                title: "Cost History",
                width: 600,
                height: 300,
                modal: true,
                buttons: [
                    {
                        text: "Close",
                        click: function() {
                            dialog.dialog('close');
                        }
                    }
                ]
            });
        }

        $(function() {

            $('#view-regular-price-history').on('click', function() {
                showPriceHistory('regular');
                return false;
            });

            $('#view-current-price-history').on('click', function() {
                showPriceHistory('current');
                return false;
            });

            $('#view-suggested-price-history').on('click', function() {
                showPriceHistory('suggested');
                return false;
            });

            $('#view-cost-history').on('click', function() {
                showCostHistory();
                return false;
            });

        });

      </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
  % if use_buefy:
        #main-product-panel {
            margin-right: 2em;
            margin-top: 1em;
        }
        #pricing-panel .field-wrapper .field {
            white-space: nowrap;
        }
  % else:
      .price-history-dialog {
          display: none;
      }
      .price-history-dialog .grid {
          color: black;
      }
  % endif
  </style>
</%def>

<%def name="render_main_fields(form)">
  ${form.render_field_readonly(product_key_field)}
  ${form.render_field_readonly('brand')}
  ${form.render_field_readonly('description')}
  ${form.render_field_readonly('size')}
  ${form.render_field_readonly('unit_size')}
  ${form.render_field_readonly('unit_of_measure')}
  ${form.render_field_readonly('average_weight')}
  ${form.render_field_readonly('case_size')}
  % if instance.is_pack_item():
      ${form.render_field_readonly('pack_size')}
      ${form.render_field_readonly('unit')}
      ${form.render_field_readonly('default_pack')}
  % elif instance.packs:
      ${form.render_field_readonly('packs')}
  % endif
  ${self.extra_main_fields(form)}
</%def>

<%def name="left_column()">
  % if use_buefy:
      <nav class="panel" id="pricing-panel">
        <p class="panel-heading">Pricing</p>
        <div class="panel-block">
          <div>
            ${self.render_price_fields(form)}
          </div>
        </div>
      </nav>
      <nav class="panel">
        <p class="panel-heading">Flags</p>
        <div class="panel-block">
          <div>
            ${self.render_flag_fields(form)}
          </div>
        </div>
      </nav>
  % else:
  <div class="panel">
    <h2>Pricing</h2>
    <div class="panel-body">
      ${self.render_price_fields(form)}
    </div>
  </div>
  <div class="panel">
    <h2>Flags</h2>
    <div class="panel-body">
      ${self.render_flag_fields(form)}
    </div>
  </div>
  % endif
  ${self.extra_left_panels()}
</%def>

<%def name="right_column()">
  ${self.organization_panel()}
  ${self.movement_panel()}
  ${self.sources_panel()}
  ${self.notes_panel()}
  ${self.ingredients_panel()}
  ${self.lookup_codes_panel()}
  ${self.extra_right_panels()}
</%def>

<%def name="extra_main_fields(form)"></%def>

<%def name="organization_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Organization</p>
        <div class="panel-block">
          <div>
            ${self.render_organization_fields(form)}
          </div>
        </div>
      </nav>
  % else:
  <div class="panel">
    <h2>Organization</h2>
    <div class="panel-body">
      ${self.render_organization_fields(form)}
    </div>
  </div>
  % endif
</%def>

<%def name="render_organization_fields(form)">
    ${form.render_field_readonly('department')}
    ${form.render_field_readonly('subdepartment')}
    ${form.render_field_readonly('category')}
    ${form.render_field_readonly('family')}
    ${form.render_field_readonly('report_code')}
</%def>

<%def name="render_price_fields(form)">
    ${form.render_field_readonly('price_required')}
    ${form.render_field_readonly('regular_price')}
    ${form.render_field_readonly('current_price')}
    ${form.render_field_readonly('current_price_ends')}
    ${form.render_field_readonly('sale_price')}
    ${form.render_field_readonly('sale_price_ends')}
    ${form.render_field_readonly('tpr_price')}
    ${form.render_field_readonly('tpr_price_ends')}
    ${form.render_field_readonly('suggested_price')}
    ${form.render_field_readonly('deposit_link')}
    ${form.render_field_readonly('tax')}
</%def>

<%def name="render_flag_fields(form)">
    ${form.render_field_readonly('weighed')}
    ${form.render_field_readonly('discountable')}
    ${form.render_field_readonly('special_order')}
    ${form.render_field_readonly('organic')}
    ${form.render_field_readonly('not_for_sale')}
    ${form.render_field_readonly('discontinued')}
    ${form.render_field_readonly('deleted')}
</%def>

<%def name="movement_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Movement</p>
        <div class="panel-block">
          <div>
            ${self.render_movement_fields(form)}
          </div>
        </div>
      </nav>
  % else:
  <div class="panel">
    <h2>Movement</h2>
    <div class="panel-body">
      ${self.render_movement_fields(form)}
    </div>
  </div>
  % endif
</%def>

<%def name="render_movement_fields(form)">
    ${form.render_field_readonly('last_sold')}
</%def>

<%def name="lookup_codes_grid()">
  % if use_buefy:
      ${lookup_codes['grid'].render_buefy_table_element(data_prop='lookupCodesData')|n}
  % else:
  <div class="grid full no-border">
    <table>
      <thead>
        <th>Seq</th>
        <th>Code</th>
      </thead>
      <tbody>
        % for code in instance._codes:
            <tr>
              <td>${code.ordinal}</td>
              <td>${code.code}</td>
            </tr>
        % endfor
      </tbody>
    </table>
  </div>
  % endif
</%def>

<%def name="lookup_codes_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Additional Lookup Codes</p>
        <div class="panel-block">
          ${self.lookup_codes_grid()}
        </div>
      </nav>
  % else:
  <div class="panel-grid" id="product-codes">
    <h2>Additional Lookup Codes</h2>
    ${self.lookup_codes_grid()}
  </div>
  % endif
</%def>

<%def name="sources_grid()">
  % if use_buefy:
      ${vendor_sources['grid'].render_buefy_table_element(data_prop='vendorSourcesData')|n}
  % else:
  <div class="grid full no-border">
    <table>
      <thead>
        <th>${costs_label_preferred}</th>
        <th>${costs_label_vendor}</th>
        <th>${costs_label_code}</th>
        <th>${costs_label_case_size}</th>
        <th>Case Cost</th>
        <th>Unit Cost</th>
        <th>Status</th>
      </thead>
      <tbody>
        % for i, cost in enumerate(instance.costs, 1):
            <tr class="${'even' if i % 2 == 0 else 'odd'}">
              <td class="center">${'X' if cost.preference == 1 else ''}</td>
              <td>
                % if request.has_perm('vendors.view'):
                    ${h.link_to(cost.vendor, request.route_url('vendors.view', uuid=cost.vendor_uuid))}
                % else:
                    ${cost.vendor}
                % endif
              </td>
              <td class="center">${cost.code or ''}</td>
              <td class="center">${h.pretty_quantity(cost.case_size)}</td>
              <td class="right">${'$ %0.2f' % cost.case_cost if cost.case_cost is not None else ''}</td>
              <td class="right">${'$ %0.4f' % cost.unit_cost if cost.unit_cost is not None else ''}</td>
              <td>${"discontinued" if cost.discontinued else "available"}</td>
            </tr>
        % endfor
      </tbody>
    </table>
  </div>
  % endif
</%def>

<%def name="sources_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">
          Vendor Sources
          % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):
              <a href="#" @click.prevent="showCostHistory()">
                (view cost history)
              </a>
          % endif
        </p>
        <div class="panel-block">
          ${self.sources_grid()}
        </div>
      </nav>
  % else:
  <div class="panel-grid" id="product-costs">
    <h2>
      Vendor Sources
      % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):
          <a id="view-cost-history" href="#">(view cost history)</a>
      % endif
    </h2>
    ${self.sources_grid()}
  </div>
  % endif
</%def>

<%def name="notes_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Notes</p>
        <div class="panel-block">
          <div class="field">${form.render_field_readonly('notes')}</div>
        </div>
      </nav>
  % else:
  <div class="panel">
    <h2>Notes</h2>
    <div class="panel-body">
      <div class="field">${form.render_field_readonly('notes')}</div>
    </div>
  </div>
  % endif
</%def>

<%def name="ingredients_panel()">
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Ingredients</p>
        <div class="panel-block">
          ${form.render_field_readonly('ingredients')}
        </div>
      </nav>
  % else:
  <div class="panel">
    <h2>Ingredients</h2>
    <div class="panel-body">
      ${form.render_field_readonly('ingredients')}
    </div>
  </div>
  % endif
</%def>

<%def name="extra_left_panels()"></%def>

<%def name="extra_right_panels()"></%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}
  % if use_buefy and request.rattail_config.versioning_enabled() and master.has_perm('versions'):

      <b-modal :active.sync="showingPriceHistory_regular"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Regular Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${regular_price_history_grid.render_buefy_table_element(data_prop='regularPriceHistoryData', loading='regularPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_regular = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingPriceHistory_current"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Current Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${current_price_history_grid.render_buefy_table_element(data_prop='currentPriceHistoryData', loading='currentPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_current = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingPriceHistory_suggested"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Suggested Price History
            </p>
          </header>
          <section class="modal-card-body">
            ${suggested_price_history_grid.render_buefy_table_element(data_prop='suggestedPriceHistoryData', loading='suggestedPriceHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingPriceHistory_suggested = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>

      <b-modal :active.sync="showingCostHistory"
               has-modal-card>
        <div class="modal-card">
          <header class="modal-card-head">
            <p class="modal-card-title">
              Cost History
            </p>
          </header>
          <section class="modal-card-body">
            ${cost_history_grid.render_buefy_table_element(data_prop='costHistoryData', loading='costHistoryLoading', paginated=True, per_page=10)|n}
          </section>
          <footer class="modal-card-foot">
            <b-button @click="showingCostHistory = false">
              Close
            </b-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="page_content()">
  % if use_buefy:
          <div style="display: flex; flex-direction: column;">

            <nav class="panel" id="main-product-panel">
              <p class="panel-heading">Product</p>
              <div class="panel-block">
                <div style="display: flex; justify-content: space-between; width: 100%;">
                  <div>
                    ${self.render_main_fields(form)}
                  </div>
                  <div>
                    % if image_url:
                        ${h.image(image_url, "Product Image", id='product-image', width=150, height=150)}
                    % endif
                  </div>
                </div>
              </div>
            </nav>

            <div style="display: flex;">
              <div class="panel-wrapper"> <!-- left column -->
                ${self.left_column()}
              </div> <!-- left column -->
              <div class="panel-wrapper" style="margin-left: 1em;"> <!-- right column -->
                ${self.right_column()}
              </div> <!-- right column -->
            </div>

          </div>

  % else:
      ## legacy / not buefy

        <div style="display: flex; flex-direction: column;">

          <div class="panel" id="product-main">
            <h2>Product</h2>
            <div class="panel-body">
              <div style="display: flex; justify-content: space-between;">
                <div>
                  ${self.render_main_fields(form)}
                </div>
                <div>
                  % if image_url:
                      ${h.image(image_url, "Product Image", id='product-image', width=150, height=150)}
                  % endif
                </div>
              </div>
            </div>
          </div>

          <div style="display: flex;">
            <div class="panel-wrapper"> <!-- left column -->
              ${self.left_column()}
            </div> <!-- left column -->
            <div class="panel-wrapper" style="margin-left: 1em;"> <!-- right column -->
              ${self.right_column()}
            </div> <!-- right column -->
          </div>

        </div>

      % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):
          <div class="price-history-dialog" id="regular-price-history-dialog">
            ${regular_price_history_grid.render_grid()|n}
          </div>
          <div class="price-history-dialog" id="current-price-history-dialog">
            ${current_price_history_grid.render_grid()|n}
          </div>
          <div class="price-history-dialog" id="suggested-price-history-dialog">
            ${suggested_price_history_grid.render_grid()|n}
          </div>
          <div class="price-history-dialog" id="cost-history-dialog">
            ${cost_history_grid.render_grid()|n}
          </div>
      % endif
  % endif

  % if buttons:
      ${buttons|n}
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.vendorSourcesData = ${json.dumps(vendor_sources['data'])|n}
    ThisPageData.lookupCodesData = ${json.dumps(lookup_codes['data'])|n}

    % if request.rattail_config.versioning_enabled() and master.has_perm('versions'):

        ThisPageData.showingPriceHistory_regular = false
        ThisPageData.regularPriceHistoryDataRaw = ${json.dumps(regular_price_history_grid.get_buefy_data()['data'])|n}
        ThisPageData.regularPriceHistoryLoading = false

        ThisPage.computed.regularPriceHistoryData = function() {
            let data = []
            this.regularPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_regular = function() {
            this.showingPriceHistory_regular = true
            this.regularPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'regular'}
            this.$http.get(url, {params: params}).then(response => {
                this.regularPriceHistoryDataRaw = response.data
                this.regularPriceHistoryLoading = false
            })
        }

        ThisPageData.showingPriceHistory_current = false
        ThisPageData.currentPriceHistoryDataRaw = ${json.dumps(current_price_history_grid.get_buefy_data()['data'])|n}
        ThisPageData.currentPriceHistoryLoading = false

        ThisPage.computed.currentPriceHistoryData = function() {
            let data = []
            this.currentPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    price_type: raw.price_type,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_current = function() {
            this.showingPriceHistory_current = true
            this.currentPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'current'}
            this.$http.get(url, {params: params}).then(response => {
                this.currentPriceHistoryDataRaw = response.data
                this.currentPriceHistoryLoading = false
            })
        }

        ThisPageData.showingPriceHistory_suggested = false
        ThisPageData.suggestedPriceHistoryDataRaw = ${json.dumps(suggested_price_history_grid.get_buefy_data()['data'])|n}
        ThisPageData.suggestedPriceHistoryLoading = false

        ThisPage.computed.suggestedPriceHistoryData = function() {
            let data = []
            this.suggestedPriceHistoryDataRaw.forEach(raw => {
                data.push({
                    price: raw.price_display,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showPriceHistory_suggested = function() {
            this.showingPriceHistory_suggested = true
            this.suggestedPriceHistoryLoading = true

            let url = '${url("products.price_history", uuid=instance.uuid)}'
            let params = {'type': 'suggested'}
            this.$http.get(url, {params: params}).then(response => {
                this.suggestedPriceHistoryDataRaw = response.data
                this.suggestedPriceHistoryLoading = false
            })
        }

        ThisPageData.showingCostHistory = false
        ThisPageData.costHistoryDataRaw = ${json.dumps(cost_history_grid.get_buefy_data()['data'])|n}
        ThisPageData.costHistoryLoading = false

        ThisPage.computed.costHistoryData = function() {
            let data = []
            this.costHistoryDataRaw.forEach(raw => {
                data.push({
                    cost: raw.cost_display,
                    vendor: raw.vendor,
                    since: raw.since,
                    changed: raw.changed_display_html,
                    changed_by: raw.changed_by_display,
                })
            })
            return data
        }

        ThisPage.methods.showCostHistory = function() {
            this.showingCostHistory = true
            this.costHistoryLoading = true

            let url = '${url("products.cost_history", uuid=instance.uuid)}'
            this.$http.get(url).then(response => {
                this.costHistoryDataRaw = response.data
                this.costHistoryLoading = false
            })
        }

    % endif
  </script>
</%def>


${parent.body()}
