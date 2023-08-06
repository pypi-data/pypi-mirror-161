## -*- coding: utf-8; -*-
<%inherit file="/batch/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/purchases.css'))}
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('{}.download_excel'.format(permission_prefix)):
      <li>${h.link_to("Download {} as Excel".format(model_title), url('{}.download_excel'.format(route_prefix), uuid=batch.uuid))}</li>
  % endif
</%def>

<%def name="render_row_grid_tools()">
  ${parent.render_row_grid_tools()}
  % if not batch.executed and not batch.complete and master.has_perm('edit_row'):
      <ordering-scanner numeric-only>
      </ordering-scanner>
  % endif
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  % if not batch.executed and not batch.complete and master.has_perm('edit_row'):
      <script type="text/x-template" id="ordering-scanner-template">
        <div>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="fas fa-play"
                    @click="startScanning()">
            Start Scanning
          </b-button>
          <b-modal :active.sync="showScanningDialog"
                   :can-cancel="false">
            <div class="card">
              <div class="card-content">
                <section style="min-height: 400px;">
                  <div class="columns">

                    <div class="column">
                      <b-field grouped>

                        <numeric-input v-if="numericOnly"
                                       v-model="itemEntry"
                                       allow-enter
                                       placeholder="Enter UPC"
                                       icon-pack="fas"
                                       icon="fas fa-search"
                                       ref="itemEntryInput"
                                       :disabled="currentRow"
                                       @keydown.native="itemEntryKeydown">
                        </numeric-input>

                        <b-input v-if="!numericOnly"
                                 v-model="itemEntry"
                                 placeholder="Enter UPC"
                                 icon-pack="fas"
                                 icon="fas fa-search"
                                 ref="itemEntryInput"
                                 :disabled="currentRow">
                        </b-input>

                        <b-button @click="fetchEntry()"
                                  :disabled="currentRow">
                          Fetch
                        </b-button>

                      </b-field>

                      <div v-if="currentRow">
                        <b-field grouped>

                          <b-field label="${enum.UNIT_OF_MEASURE[enum.UNIT_OF_MEASURE_CASE]}" horizontal>
                            <numeric-input v-model="currentRow.cases_ordered"
                                           ref="casesInput"
                                           @keydown.native="casesKeydown"
                                           style="width: 60px; margin-right: 1rem;">
                            </numeric-input>
                          </b-field>

                          <b-field :label="currentRow.unit_of_measure_display" horizontal>
                            <numeric-input v-model="currentRow.units_ordered"
                                           ref="unitsInput"
                                           @keydown.native="unitsKeydown"
                                           style="width: 60px;">
                            </numeric-input>
                          </b-field>

                        </b-field>

                        <p class="block has-text-weight-bold">
                          1 ${enum.UNIT_OF_MEASURE[enum.UNIT_OF_MEASURE_CASE]}
                          = {{ currentRow.case_quantity || '??' }}
                          {{ currentRow.unit_of_measure_display }}
                        </p>

                        <p class="block has-text-weight-bold">
                          {{ currentRow.po_case_cost_display || '$?.??' }}
                          per ${enum.UNIT_OF_MEASURE[enum.UNIT_OF_MEASURE_CASE]};
                          {{ currentRow.po_unit_cost_display || '$?.??' }}
                          per {{ currentRow.unit_of_measure_display }}
                        </p>

                        <p class="block has-text-weight-bold">
                          Total is
                          {{ totalCostDisplay }}
                        </p>

                        <div class="buttons">
                          <b-button type="is-primary"
                                    icon-pack="fas"
                                    icon-left="fas fa-save"
                                    @click="saveCurrentRow()">
                            Save
                          </b-button>
                          <b-button @click="cancelCurrentRow()">
                            Cancel
                          </b-button>
                        </div>
                      </div>

                    </div>

                    <div class="column is-three-fifths">
                      <div v-if="currentRow">

                        <b-field label="UPC" horizontal>
                          {{ currentRow.upc_display }}
                        </b-field>

                        <b-field label="Brand" horizontal>
                          {{ currentRow.brand_name }}
                        </b-field>

                        <b-field label="Description" horizontal>
                          {{ currentRow.description }}
                        </b-field>

                        <b-field label="Size" horizontal>
                          {{ currentRow.size }}
                        </b-field>

                        <b-field label="Reg. Price" horizontal>
                          {{ currentRow.product_price_display }}
                        </b-field>

                        <div class="buttons">
                          <img :src="currentRow.image_url"></img>
                          <b-button v-if="currentRow.product_url"
                                    type="is-primary"
                                    tag="a" :href="currentRow.product_url"
                                    target="_blank">
                            View Full Product
                          </b-button>
                        </div>
                      </div>
                    </div>

                  </div> <!-- columns -->
                </section>

                <div class="level">
                  <div class="level-left">
                  </div>
                  <div class="level-right">
                    <div class="level-item buttons">
                      <once-button type="is-primary"
                                   @click="stopScanning()"
                                   text="Stop Scanning"
                                   icon-left="stop"
                                   :disabled="currentRow"
                                   :title="currentRow ? 'Please save or cancel first' : null">
                      </once-button>
                    </div>
                  </div>
                </div>

              </div> <!-- card-content -->
            </div>
          </b-modal>
        </div>
      </script>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if not batch.executed and not batch.complete and master.has_perm('edit_row'):
      <script type="text/javascript">

        let OrderingScanner = {
            template: '#ordering-scanner-template',
            props: {
                numericOnly: Boolean,
            },
            data() {
                return {
                    showScanningDialog: false,
                    itemEntry: null,
                    fetching: false,
                    currentRow: null,
                    saving: false,

                    ## TODO: should find a better way to handle CSRF token
                    csrftoken: ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n},
                }
            },
            computed: {

                totalUnits() {
                    let cases = parseFloat(this.currentRow.cases_ordered || 0)
                    let units = parseFloat(this.currentRow.units_ordered || 0)
                    if (cases) {
                        units += cases * (this.currentRow.case_quantity || 1)
                    }
                    return units
                },

                totalUnitsDisplay() {
                    let cases = parseFloat(this.currentRow.cases_ordered || 0)
                    let units = parseFloat(this.currentRow.units_ordered || 0)
                    let casesTotal = ""
                    if (cases) {
                        casesTotal = cases.toString() + " ${enum.UNIT_OF_MEASURE[enum.UNIT_OF_MEASURE_CASE]}"
                    }
                    let unitsTotal = ""
                    if (units) {
                        unitsTotal = units.toString() + " " + this.currentRow.unit_of_measure_display
                    }
                    if (casesTotal.length && unitsTotal.length) {
                        return casesTotal + " + " + unitsTotal
                    } else if (casesTotal.length) {
                        return casesTotal
                    } else if (unitsTotal.length) {
                        return unitsTotal
                    }
                    return "??"
                },

                totalCost() {
                    if (this.currentRow.po_case_cost === null
                        && this.currentRow.po_unit_cost === null) {
                        return null
                    }
                    let cases = parseFloat(this.currentRow.cases_ordered || 0)
                    let units = parseFloat(this.currentRow.units_ordered || 0)
                    let total = cases * this.currentRow.po_case_cost
                    total += units * this.currentRow.po_unit_cost
                    return total
                },

                totalCostDisplay() {
                    if (this.totalCost === null) {
                        return '$?.??'
                    }
                    return '$' + this.totalCost.toFixed(2)
                },
            },
            methods: {

                startScanning() {
                    this.showScanningDialog = true
                    this.$nextTick(() => {
                        this.$refs.itemEntryInput.focus()
                    })
                },

                itemEntryKeydown(event) {
                    if (event.which == 13) {
                        this.fetchEntry()
                    }
                },

                fetchEntry() {
                    if (this.fetching) {
                        return
                    }
                    if (!this.itemEntry) {
                        return
                    }

                    this.fetching = true

                    let url = '${url('{}.scanning_entry'.format(route_prefix), uuid=batch.uuid)}'

                    let params = {
                        entry: this.itemEntry,
                    }

                    let headers = {
                        ## TODO: should find a better way to handle CSRF token
                        'X-CSRF-TOKEN': this.csrftoken,
                    }

                    ## TODO: should find a better way to handle CSRF token
                    this.$http.post(url, params, {headers: headers}).then(({ data }) => {
                        if (data.error) {
                            this.$buefy.toast.open({
                                message: "Fetch failed:  " + data.error,
                                type: 'is-danger',
                                duration: 4000, // 4 seconds
                            })
                        } else {
                            this.currentRow = data.row
                            this.$nextTick(() => {
                                this.$refs.casesInput.focus()
                            })
                        }
                        this.fetching = false
                    }, response => {
                        this.$buefy.toast.open({
                            message: "Fetch failed:  (unknown error)",
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        this.fetching = false
                    })
                },

                casesKeydown(event) {
                    if (event.which == 13) {
                        this.$refs.unitsInput.focus()
                    } else if (event.which == 27) {
                        this.cancelCurrentRow()
                    }
                },

                unitsKeydown(event) {
                    if (event.which == 13) {
                        this.saveCurrentRow()
                    } else if (event.which == 27) {
                        this.cancelCurrentRow()
                    }
                },

                saveCurrentRow() {
                    if (this.saving) {
                        return
                    }

                    this.saving = true

                    let url = '${url('{}.scanning_update'.format(route_prefix), uuid=batch.uuid)}'

                    let params = {
                        row_uuid: this.currentRow.uuid,
                        cases_ordered: this.currentRow.cases_ordered,
                        units_ordered: this.currentRow.units_ordered,
                    }

                    let headers = {
                        ## TODO: should find a better way to handle CSRF token
                        'X-CSRF-TOKEN': this.csrftoken,
                    }

                    ## TODO: should find a better way to handle CSRF token
                    this.$http.post(url, params, {headers: headers}).then(({ data }) => {
                        if (data.error) {
                            this.$buefy.toast.open({
                                message: "Save failed:  " + data.error,
                                type: 'is-danger',
                                duration: 4000, // 4 seconds
                            })
                        } else {
                            this.$buefy.toast.open({
                                message: "Item was saved",
                                type: 'is-success',
                            })
                            this.itemEntry = null
                            this.currentRow = null
                            this.$nextTick(() => {
                                this.$refs.itemEntryInput.focus()
                            })
                        }
                        this.saving = false
                    }, response => {
                        this.$buefy.toast.open({
                            message: "Save failed:  (unknown error)",
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        this.saving = false
                    })

                },

                cancelCurrentRow() {
                    this.itemEntry = null
                    this.currentRow = null
                    this.$buefy.toast.open({
                        message: "Edit was cancelled",
                        type: 'is-warning',
                    })
                    this.$nextTick(() => {
                        this.$refs.itemEntryInput.focus()
                    })
                },

                stopScanning() {
                    location.reload()
                },
            }
        }

      </script>
  % endif
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  % if not batch.executed and not batch.complete and master.has_perm('edit_row'):
      <script type="text/javascript">

        Vue.component('ordering-scanner', OrderingScanner)

      </script>
  % endif
</%def>


${parent.body()}
