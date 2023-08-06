## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="render_buefy_form()">
  <div class="form">
    <${form.component} ref="mainForm"
                       % if master.has_perm('confirm_price'):
                       @confirm-price="showConfirmPrice"
                       % endif
                       % if master.has_perm('change_status'):
                       @change-status="showChangeStatus"
                       % endif
                       % if master.has_perm('add_note'):
                       @add-note="showAddNote"
                       % endif
                       >
    </${form.component}>
  </div>
</%def>

<%def name="page_content()">
  ${parent.page_content()}

  % if master.has_perm('confirm_price'):
      <b-modal has-modal-card
               :active.sync="confirmPriceShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Confirm Price</p>
          </header>

          <section class="modal-card-body">
            <p>
              Please provide a note</span>:
            </p>
            <b-input v-model="confirmPriceNote"
                     ref="confirmPriceNoteField"
                     type="textarea" rows="2">
            </b-input>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="confirmPriceSave()"
                      :disabled="confirmPriceSaveDisabled"
                      icon-pack="fas"
                      icon-left="check">
              {{ confirmPriceSubmitText }}
            </b-button>
            <b-button @click="confirmPriceShowDialog = false">
              Cancel
            </b-button>
          </footer>
        </div>
      </b-modal>
      ${h.form(master.get_action_url('confirm_price', instance), ref='confirmPriceForm')}
      ${h.csrf_token(request)}
      ${h.hidden('note', **{':value': 'confirmPriceNote'})}
      ${h.end_form()}
  % endif

  % if master.has_perm('change_status'):
      <b-modal :active.sync="showChangeStatusDialog">
        <div class="card">
          <div class="card-content">
            <div class="level">
              <div class="level-left">

                <div class="level-item">
                  Current status is:&nbsp;
                </div>

                <div class="level-item has-text-weight-bold">
                  {{ orderItemStatuses[oldStatusCode] }}
                </div>

                <div class="level-item"
                     style="margin-left: 5rem;">
                  New status will be:
                </div>

                <b-field class="level-item"
                         :type="newStatusCode ? null : 'is-danger'">
                  <b-select v-model="newStatusCode">
                    <option v-for="item in orderItemStatusOptions"
                            :key="item.key"
                            :value="item.key">
                      {{ item.label }}
                    </option>
                  </b-select>
                </b-field>

              </div>
            </div>

            <div v-if="changeStatusGridData.length">

              <p class="block">
                Please indicate any other item(s) to which the new
                status should be applied:
              </p>

              <b-table :data="changeStatusGridData"
                       checkable 
                       :checked-rows.sync="changeStatusCheckedRows"
                       narrowed 
                       class="is-size-7">
                <template slot-scope="props">
                  <b-table-column field="product_brand" label="Brand">
                    <span v-html="props.row.product_brand"></span>
                  </b-table-column>
                  <b-table-column field="product_description" label="Product">
                    <span v-html="props.row.product_description"></span>
                  </b-table-column>
                  <!-- <b-table-column field="quantity" label="Quantity"> -->
                  <!--   <span v-html="props.row.quantity"></span> -->
                  <!-- </b-table-column> -->
                  <b-table-column field="product_case_quantity" label="cPack">
                    <span v-html="props.row.product_case_quantity"></span>
                  </b-table-column>
                  <b-table-column field="order_quantity" label="oQty">
                    <span v-html="props.row.order_quantity"></span>
                  </b-table-column>
                  <b-table-column field="order_uom" label="UOM">
                    <span v-html="props.row.order_uom"></span>
                  </b-table-column>
                  <b-table-column field="department_name" label="Department">
                    <span v-html="props.row.department_name"></span>
                  </b-table-column>
                  <b-table-column field="product_barcode" label="Product Barcode">
                    <span v-html="props.row.product_barcode"></span>
                  </b-table-column>
                  <b-table-column field="unit_price" label="Unit $">
                    <span v-html="props.row.unit_price"></span>
                  </b-table-column>
                  <b-table-column field="total_price" label="Total $">
                    <span v-html="props.row.total_price"></span>
                  </b-table-column>
                  <b-table-column field="order_date" label="Order Date">
                    <span v-html="props.row.order_date"></span>
                  </b-table-column>
                  <b-table-column field="status_code" label="Status">
                    <span v-html="props.row.status_code"></span>
                  </b-table-column>
                  <!-- <b-table-column field="flagged" label="Flagged"> -->
                  <!--   <span v-html="props.row.flagged"></span> -->
                  <!-- </b-table-column> -->
                </template>
              </b-table>

              <br />
            </div>

            <p>
              Please provide a note<span v-if="changeStatusGridData.length">
                (will be applied to all selected items)</span>:
            </p>
            <b-input v-model="newStatusNote"
                     type="textarea" rows="2">
            </b-input>

            <br />

            <div class="buttons">
              <b-button type="is-primary"
                        :disabled="changeStatusSaveDisabled"
                        icon-pack="fas"
                        icon-left="save"
                        @click="statusChangeSave()">
                {{ changeStatusSubmitText }}
              </b-button>
              <b-button @click="cancelStatusChange">
                Cancel
              </b-button>
            </div>

          </div>
        </div>
      </b-modal>
      ${h.form(master.get_action_url('change_status', instance), ref='changeStatusForm')}
      ${h.csrf_token(request)}
      ${h.hidden('new_status_code', **{'v-model': 'newStatusCode'})}
      ${h.hidden('uuids', **{':value': 'changeStatusCheckedRows.map((row) => {return row.uuid}).join()'})}
      ${h.hidden('note', **{':value': 'newStatusNote'})}
      ${h.end_form()}
  % endif

  % if master.has_perm('add_note'):
      <b-modal has-modal-card
               :active.sync="showAddNoteDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Add Note</p>
          </header>

          <section class="modal-card-body">
            <b-field>
              <b-input type="textarea" rows="8"
                       v-model="newNoteText"
                       ref="newNoteTextArea">
              </b-input>
            </b-field>
            <b-field>
              <b-checkbox v-model="newNoteApplyAll">
                Apply to all items on this order
              </b-checkbox>
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button type="is-primary"
                      @click="addNoteSave()"
                      :disabled="addNoteSaveDisabled"
                      icon-pack="fas"
                      icon-left="save">
              {{ addNoteSubmitText }}
            </b-button>
            <b-button @click="showAddNoteDialog = false">
              Cancel
            </b-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ${form.component_studly}Data.notesData = ${json.dumps(notes_data)|n}

    % if master.has_perm('confirm_price'):

        ThisPageData.confirmPriceShowDialog = false
        ThisPageData.confirmPriceNote = null
        ThisPageData.confirmPriceSubmitting = false

        ThisPage.computed.confirmPriceSaveDisabled = function() {
            if (this.confirmPriceSubmitting) {
                return true
            }
            return false
        }

        ThisPage.computed.confirmPriceSubmitText = function() {
            if (this.confirmPriceSubmitting) {
                return "Working, please wait..."
            }
            return "Confirm Price"
        }

        ThisPage.methods.showConfirmPrice = function() {
            this.confirmPriceNote = null
            this.confirmPriceShowDialog = true
            this.$nextTick(() => {
                this.$refs.confirmPriceNoteField.focus()
            })
        }

        ThisPage.methods.confirmPriceSave = function() {
            this.confirmPriceSubmitting = true
            this.$refs.confirmPriceForm.submit()
        }

    % endif

    % if master.has_perm('change_status'):

        ThisPageData.orderItemStatuses = ${json.dumps(enum.CUSTORDER_ITEM_STATUS)|n}
        ThisPageData.orderItemStatusOptions = ${json.dumps([dict(key=k, label=v) for k, v in six.iteritems(enum.CUSTORDER_ITEM_STATUS)])|n}

        ThisPageData.oldStatusCode = ${instance.status_code}

        ThisPageData.showChangeStatusDialog = false
        ThisPageData.newStatusCode = null
        ThisPageData.changeStatusGridData = ${json.dumps(other_order_items_data)|n}
        ThisPageData.changeStatusCheckedRows = []
        ThisPageData.newStatusNote = null
        ThisPageData.changeStatusSubmitText = "Update Status"
        ThisPageData.changeStatusSubmitting = false

        ThisPage.computed.changeStatusSaveDisabled = function() {
            if (!this.newStatusCode) {
                return true
            }
            if (this.changeStatusSubmitting) {
                return true
            }
            return false
        }

        ThisPage.methods.showChangeStatus = function() {
            this.newStatusCode = null
            // clear out any checked rows
            this.changeStatusCheckedRows.length = 0
            this.newStatusNote = null
            this.showChangeStatusDialog = true
        }

        ThisPage.methods.cancelStatusChange = function() {
            this.showChangeStatusDialog = false
        }

        ThisPage.methods.statusChangeSave = function() {
            if (this.newStatusCode == this.oldStatusCode) {
                alert("You chose the same status it already had...")
                return
            }

            this.changeStatusSubmitting = true
            this.changeStatusSubmitText = "Working, please wait..."
            this.$refs.changeStatusForm.submit()
        }

    % endif

    % if master.has_perm('add_note'):

        ThisPageData.showAddNoteDialog = false
        ThisPageData.newNoteText = null
        ThisPageData.newNoteApplyAll = false
        ThisPageData.addNoteSubmitting = false
        ThisPageData.addNoteSubmitText = "Save Note"

        ThisPage.computed.addNoteSaveDisabled = function() {
            if (!this.newNoteText) {
                return true
            }
            if (this.addNoteSubmitting) {
                return true
            }
            return false
        }

        ThisPage.methods.showAddNote = function() {
            this.newNoteText = null
            this.newNoteApplyAll = false
            this.showAddNoteDialog = true
            this.$nextTick(() => {
                this.$refs.newNoteTextArea.focus()
            })
        }

        ThisPage.methods.addNoteSave = function() {
            this.addNoteSubmitting = true
            this.addNoteSubmitText = "Working, please wait..."

            let url = '${url('{}.add_note'.format(route_prefix), uuid=instance.uuid)}'

            let params = {
                note: this.newNoteText,
                apply_all: this.newNoteApplyAll,
            }

            let headers = {
                ## TODO: should find a better way to handle CSRF token
                'X-CSRF-TOKEN': this.csrftoken,
            }

            ## TODO: should find a better way to handle CSRF token
            this.$http.post(url, params, {headers: headers}).then(({ data }) => {
                if (data.success) {
                    this.$refs.mainForm.notesData = data.notes
                    this.showAddNoteDialog = false
                } else {
                    this.$buefy.toast.open({
                        message: "Save failed:  " + (data.error || "(unknown error)"),
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                }
                this.addNoteSubmitting = false
                this.addNoteSubmitText = "Save Note"
            }).catch((error) => {
                // TODO: should handle this better somehow..?
                this.$buefy.toast.open({
                    message: "Save failed:  (unknown error)",
                    type: 'is-danger',
                    duration: 4000, // 4 seconds
                })
                this.addNoteSubmitting = false
                this.addNoteSubmitText = "Save Note"
            })
        }

    % endif

  </script>
</%def>

${parent.body()}
