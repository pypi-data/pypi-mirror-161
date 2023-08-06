## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">
  ${h.hidden('handlers', **{':value': 'JSON.stringify(handlersData)'})}

  <h3 class="is-size-3">Designated Handlers</h3>

  <b-table :data="handlersData"
           narrowed
           icon-pack="fas"
           :default-sort="['host_title', 'asc']">
      <template slot-scope="props">
        <b-table-column field="host_title" label="Data Source" sortable>
          {{ props.row.host_title }}
        </b-table-column>
        <b-table-column field="local_title" label="Data Target" sortable>
          {{ props.row.local_title }}
        </b-table-column>
        <b-table-column field="direction" label="Direction" sortable>
          {{ props.row.direction_display }}
        </b-table-column>
        <b-table-column field="handler_spec" label="Handler Spec" sortable>
          {{ props.row.handler_spec }}
        </b-table-column>
        <b-table-column field="cmd" label="Command" sortable>
          {{ props.row.command }} {{ props.row.subcommand }}
        </b-table-column>
        <b-table-column field="runas" label="Default Runas" sortable>
          {{ props.row.default_runas }}
        </b-table-column>
        <b-table-column label="Actions">
          <a href="#" class="grid-action"
             @click.prevent="editHandler(props.row)">
            <i class="fas fa-edit"></i>
            Edit
          </a>          
        </b-table-column>
      </template>
      <template slot="empty">
        <section class="section">
          <div class="content has-text-grey has-text-centered">
            <p>
              <b-icon
                 pack="fas"
                 icon="fas fa-sad-tear"
                 size="is-large">
              </b-icon>
            </p>
            <p>Nothing here.</p>
          </div>
        </section>
      </template>
  </b-table>
  
  <b-modal :active.sync="editHandlerShowDialog">
    <div class="card">
      <div class="card-content">

        <b-field :label="editingHandlerDirection" horizontal expanded>
          {{ editingHandlerHostTitle }} -> {{ editingHandlerLocalTitle }}
        </b-field>

        <b-field label="Handler Spec"
                 :type="editingHandlerSpec ? null : 'is-danger'">
          <b-select v-model="editingHandlerSpec">
            <option v-for="option in editingHandlerSpecOptions"
                    :key="option"
                    :value="option">
              {{ option }}
            </option>
          </b-select>
        </b-field>

        <b-field grouped>
          
          <b-field label="Command"
                   :type="editingHandlerCommand ? null : 'is-danger'">
            <div class="level">
              <div class="level-left">
                <div class="level-item" style="margin-right: 0;">
                  bin/
                </div>
                <div class="level-item" style="margin-left: 0;">
                  <b-input v-model="editingHandlerCommand">
                  </b-input>
                </div>
              </div>
            </div>
          </b-field>

          <b-field label="Subcommand"
                   :type="editingHandlerSubcommand ? null : 'is-danger'">
            <b-input v-model="editingHandlerSubcommand">
            </b-input>
          </b-field>

          <b-field label="Default Runas">
            <b-input v-model="editingHandlerRunas">
            </b-input>
          </b-field>

        </b-field>

        <b-field grouped>

          <b-button @click="editHandlerShowDialog = false"
                    class="control">
            Cancel
          </b-button>

          <b-button type="is-primary"
                    class="control"
                    @click="updateHandler()"
                    :disabled="updateHandlerDisabled">
            Update Handler
          </b-button>

        </b-field>

      </div>
    </div>
  </b-modal>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.handlersData = ${json.dumps(handlers_data)|n}

    ThisPageData.editHandlerShowDialog = false
    ThisPageData.editingHandler = null
    ThisPageData.editingHandlerHostTitle = null
    ThisPageData.editingHandlerLocalTitle = null
    ThisPageData.editingHandlerDirection = 'import'
    ThisPageData.editingHandlerSpec = null
    ThisPageData.editingHandlerSpecOptions = []
    ThisPageData.editingHandlerCommand = null
    ThisPageData.editingHandlerSubcommand = null
    ThisPageData.editingHandlerRunas = null

    ThisPage.computed.updateHandlerDisabled = function() {
        if (!this.editingHandlerSpec) {
            return true
        }
        if (!this.editingHandlerCommand) {
            return true
        }
        if (!this.editingHandlerSubcommand) {
            return true
        }
        return false
    }

    ThisPage.methods.editHandler = function(row) {
        this.editingHandler = row

        this.editingHandlerHostTitle = row.host_title
        this.editingHandlerLocalTitle = row.local_title
        this.editingHandlerDirection = row.direction_display
        this.editingHandlerSpec = row.handler_spec
        this.editingHandlerSpecOptions = row.spec_options
        this.editingHandlerCommand = row.command
        this.editingHandlerSubcommand = row.subcommand
        this.editingHandlerRunas = row.default_runas

        this.editHandlerShowDialog = true
    }

    ThisPage.methods.updateHandler = function() {
        let row = this.editingHandler

        row.handler_spec = this.editingHandlerSpec
        row.command = this.editingHandlerCommand
        row.subcommand = this.editingHandlerSubcommand
        row.default_runas = this.editingHandlerRunas

        this.settingsNeedSaved = true
        this.editHandlerShowDialog = false
    }

  </script>
</%def>


${parent.body()}
