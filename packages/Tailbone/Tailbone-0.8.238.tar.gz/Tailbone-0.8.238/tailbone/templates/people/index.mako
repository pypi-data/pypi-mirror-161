## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">

  % if master.mergeable and master.has_perm('request_merge'):
      % if use_buefy:
      <b-button @click="showMergeRequest()"
                icon-pack="fas"
                icon-left="object-ungroup"
                :disabled="checkedRows.length != 2">
        Request Merge
      </b-button>
      <b-modal has-modal-card
               :active.sync="mergeRequestShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Request Merge of 2 People</p>
          </header>

          <section class="modal-card-body">
            <b-table :data="mergeRequestRows"
                     striped hoverable>
              <template slot-scope="props">
                <b-table-column field="customer_number"
                                label="Customer #">
                  <span v-html="props.row.customer_number"></span>
                </b-table-column>
                <b-table-column field="first_name"
                                label="First Name">
                  <span v-html="props.row.first_name"></span>
                </b-table-column>
                <b-table-column field="last_name"
                                label="Last Name">
                  <span v-html="props.row.last_name"></span>
                </b-table-column>
              </template>
            </b-table>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="mergeRequestShowDialog = false">
              Cancel
            </b-button>
            ${h.form(url('{}.request_merge'.format(route_prefix)), **{'@submit': 'submitMergeRequest'})}
            ${h.csrf_token(request)}
            ${h.hidden('removing_uuid', **{':value': 'mergeRequestRemovingUUID'})}
            ${h.hidden('keeping_uuid', **{':value': 'mergeRequestKeepingUUID'})}
            <b-button type="is-primary"
                      native-type="submit"
                      :disabled="mergeRequestSubmitting">
              {{ mergeRequestSubmitText }}
            </b-button>
            ${h.end_form()}
          </footer>
        </div>
      </b-modal>
      % endif
  % endif

  ${parent.grid_tools()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    % if master.mergeable and master.has_perm('request_merge'):

        ${grid.component_studly}Data.mergeRequestShowDialog = false
        ${grid.component_studly}Data.mergeRequestRows = []
        ${grid.component_studly}Data.mergeRequestSubmitText = "Submit Merge Request"
        ${grid.component_studly}Data.mergeRequestSubmitting = false

        ${grid.component_studly}.computed.mergeRequestRemovingUUID = function() {
            if (this.mergeRequestRows.length) {
                return this.mergeRequestRows[0].uuid
            }
            return null
        }

        ${grid.component_studly}.computed.mergeRequestKeepingUUID = function() {
            if (this.mergeRequestRows.length) {
                return this.mergeRequestRows[1].uuid
            }
            return null
        }

        ${grid.component_studly}.methods.showMergeRequest = function() {
            this.mergeRequestRows = this.checkedRows
            this.mergeRequestShowDialog = true
        }

        ${grid.component_studly}.methods.submitMergeRequest = function() {
            this.mergeRequestSubmitting = true
            this.mergeRequestSubmitText = "Working, please wait..."
        }

    % endif

  </script>
</%def>

${parent.body()}
