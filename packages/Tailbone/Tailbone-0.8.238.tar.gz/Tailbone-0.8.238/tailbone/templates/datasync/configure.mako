## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="buttons_row()">
  <div class="level">
    <div class="level-left">

      <div class="level-item">
        <p class="block">
          This tool lets you modify the DataSync configuration.&nbsp;
          Before using it,
          <a href="#" class="has-background-warning"
             @click.prevent="showConfigFilesNote = !showConfigFilesNote">
            please see these notes.
          </a>
        </p>
      </div>

      <div class="level-item">
        ${self.save_undo_buttons()}
      </div>
    </div>

    <div class="level-right">

      <div class="level-item">
        ${h.form(url('datasync.restart'), **{'@submit': 'submitRestartDatasyncForm'})}
        ${h.csrf_token(request)}
        <b-button type="is-primary"
                  native-type="submit"
                  @click="restartDatasync"
                  :disabled="restartingDatasync"
                  icon-pack="fas"
                  icon-left="redo">
          {{ restartDatasyncFormButtonText }}
        </b-button>
        ${h.end_form()}
      </div>

      <div class="level-item">
        ${self.purge_button()}
      </div>
    </div>
  </div>
</%def>

<%def name="form_content()">
  ${h.hidden('profiles', **{':value': 'JSON.stringify(profilesData)'})}

  <b-notification type="is-warning"
                  :active.sync="showConfigFilesNote">
    ## TODO: should link to some ratman page here, yes?
    <p class="block">
      This tool works by modifying settings in the DB.&nbsp; It
      does <span class="is-italic">not</span> modify any config
      files.&nbsp; If you intend to manage datasync config via files
      only then you should
      <span class="is-italic">not</span> use this tool!
    </p>
    <p class="block">
      If you have managed config via files thus far, and want to use
      this tool anyway/instead, that&apos;s fine - but after saving
      the settings via this tool you should probably remove all
      <span class="is-family-code">[rattail.datasync]</span> entries
      from your config file (and restart apps) so as to avoid
      confusion.
    </p>
    <p class="block">
      Finally, you should know that this tool will
      <span class="is-italic">overwrite</span> the entire
      <span class="is-family-code">rattail.datasync</span> namespace
      within the DB settings.&nbsp; In other words if you have
      manually created any ${h.link_to("Raw Settings", url('settings'))}
      within that namepsace, they will be lost when you save settings
      with this tool.
    </p>
  </b-notification>

  <div class="level">
    <div class="level-left">
      <div class="level-item">
        <h3 class="is-size-3">Watcher Profiles</h3>
      </div>
    </div>
    <div class="level-right">
      <div class="level-item">
        <b-button type="is-primary"
                  @click="newProfile()"
                  icon-pack="fas"
                  icon-left="plus">
          New Profile
        </b-button>
      </div>
      <div class="level-item">
        <b-button @click="toggleDisabledProfiles()">
          {{ showDisabledProfiles ? "Hide" : "Show" }} Disabled
        </b-button>
      </div>
    </div>
  </div>

  <b-table :data="filteredProfilesData"
           :row-class="(row, i) => row.enabled ? null : 'has-background-warning'">
      <template slot-scope="props">
        <b-table-column field="key" label="Watcher Key">
          {{ props.row.key }}
        </b-table-column>
        <b-table-column field="watcher_spec" label="Watcher Spec">
          {{ props.row.watcher_spec }}
        </b-table-column>
        <b-table-column field="watcher_dbkey" label="DB Key">
          {{ props.row.watcher_dbkey }}
        </b-table-column>
        <b-table-column field="watcher_delay" label="Loop Delay">
          {{ props.row.watcher_delay }} sec
        </b-table-column>
        <b-table-column field="watcher_retry_attempts" label="Attempts / Delay">
          {{ props.row.watcher_retry_attempts }} / {{ props.row.watcher_retry_delay }} sec
        </b-table-column>
        <b-table-column field="watcher_default_runas" label="Default Runas">
          {{ props.row.watcher_default_runas }}
        </b-table-column>
        <b-table-column label="Consumers">
          {{ consumerShortList(props.row) }}
        </b-table-column>
##         <b-table-column field="notes" label="Notes">
##           TODO
##           ## {{ props.row.notes }}
##         </b-table-column>
        <b-table-column field="enabled" label="Enabled">
          {{ props.row.enabled ? "Yes" : "No" }}
        </b-table-column>
        <b-table-column label="Actions">
          <a href="#"
             class="grid-action"
             @click.prevent="editProfile(props.row)">
            <i class="fas fa-edit"></i>
            Edit
          </a>          
          &nbsp;
          <a href="#"
             class="grid-action has-text-danger"
             @click.prevent="deleteProfile(props.row)">
            <i class="fas fa-trash"></i>
            Delete
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

  <b-modal :active.sync="editProfileShowDialog">
    <div class="card">
      <div class="card-content">

        <b-field grouped>
          
          <b-field label="Watcher Key"
                   :type="editingProfileKey ? null : 'is-danger'">
            <b-input v-model="editingProfileKey"
                     ref="watcherKeyInput">
            </b-input>
          </b-field>

          <b-field label="Default Runas User">
            <b-input v-model="editingProfileWatcherDefaultRunas">
            </b-input>
          </b-field>

        </b-field>

        <b-field grouped>

          <b-field label="Watcher Spec" 
                   :type="editingProfileWatcherSpec ? null : 'is-danger'"
                   expanded>
            <b-input v-model="editingProfileWatcherSpec">
            </b-input>
          </b-field>

          <b-field label="DB Key">
            <b-input v-model="editingProfileWatcherDBKey">
            </b-input>
          </b-field>

        </b-field>

        <b-field grouped>

          <b-field label="Loop Delay (seconds)">
            <b-input v-model="editingProfileWatcherDelay">
            </b-input>
          </b-field>

          <b-field label="Attempts">
            <b-input v-model="editingProfileWatcherRetryAttempts">
            </b-input>
          </b-field>

          <b-field label="Retry Delay (seconds)">
            <b-input v-model="editingProfileWatcherRetryDelay">
            </b-input>
          </b-field>

        </b-field>

        <div style="display: flex;">

          <div style="width: 40%;">

            <b-field label="Watcher consumes its own changes"
                     v-if="!editingProfilePendingConsumers.length">
              <b-checkbox v-model="editingProfileWatcherConsumesSelf">
                {{ editingProfileWatcherConsumesSelf ? "Yes" : "No" }}
              </b-checkbox>
            </b-field>

            <b-table :data="editingProfilePendingConsumers"
                     v-if="!editingProfileWatcherConsumesSelf"
                     :row-class="(row, i) => row.enabled ? null : 'has-background-warning'">
              <template slot-scope="props">
                <b-table-column field="key" label="Consumer">
                  {{ props.row.key }}
                </b-table-column>
                <b-table-column style="white-space: nowrap;">
                  {{ props.row.consumer_delay }} / {{ props.row.consumer_retry_attempts }} / {{ props.row.consumer_retry_delay }}
                </b-table-column>
                <b-table-column label="Actions">
                  <a href="#"
                     class="grid-action"
                     @click.prevent="editProfileConsumer(props.row)">
                    <i class="fas fa-edit"></i>
                    Edit
                  </a>          
                  &nbsp;
                  <a href="#"
                     class="grid-action has-text-danger"
                     @click.prevent="deleteProfileConsumer(props.row)">
                    <i class="fas fa-trash"></i>
                    Delete
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

          </div>

          <div v-show="!editingConsumer && !editingProfileWatcherConsumesSelf"
               style="padding-left: 1rem;">
            <b-button type="is-primary"
                      @click="newConsumer()"
                      icon-pack="fas"
                      icon-left="plus">
              New Consumer
            </b-button>
          </div>

          <div v-show="editingConsumer"
               style="flex-grow: 1; padding-left: 1rem; padding-right: 1rem;">
            
            <b-field grouped>

              <b-field label="Consumer Key"
                       :type="editingConsumerKey ? null : 'is-danger'">
                <b-input v-model="editingConsumerKey"
                         ref="consumerKeyInput">
                </b-input>
              </b-field>

              <b-field label="Runas User">
                <b-input v-model="editingConsumerRunas">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-field label="Consumer Spec" 
                       expanded
                       :type="editingConsumerSpec ? null : 'is-danger'"
                       >
                <b-input v-model="editingConsumerSpec">
                </b-input>
              </b-field>

              <b-field label="DB Key">
                <b-input v-model="editingConsumerDBKey">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-field label="Loop Delay">
                <b-input v-model="editingConsumerDelay"
                         style="width: 8rem;">
                </b-input>
              </b-field>

              <b-field label="Attempts">
                <b-input v-model="editingConsumerRetryAttempts"
                         style="width: 8rem;">
                </b-input>
              </b-field>

              <b-field label="Retry Delay">
                <b-input v-model="editingConsumerRetryDelay"
                         style="width: 8rem;">
                </b-input>
              </b-field>

            </b-field>

            <b-field grouped>

              <b-button @click="editingConsumer = null"
                        class="control">
                Cancel
              </b-button>

              <b-button type="is-primary"
                        @click="updateConsumer()"
                        :disabled="updateConsumerDisabled"
                        class="control">
                Update Consumer
              </b-button>

              <b-field label="Enabled" horizontal
                       style="margin-left: 2rem;">
                <b-checkbox v-model="editingConsumerEnabled">
                  {{ editingConsumerEnabled ? "Yes" : "No" }}
                </b-checkbox>
              </b-field>

            </b-field>
          </div>
        </div>

        <br />
        <b-field grouped>

          <b-button @click="editProfileShowDialog = false"
                    class="control">
            Cancel
          </b-button>

          <b-button type="is-primary"
                    class="control"
                    @click="updateProfile()"
                    :disabled="updateProfileDisabled">
            Update Profile
          </b-button>

          <b-field label="Enabled" horizontal
                   style="margin-left: 2rem;">
            <b-checkbox v-model="editingProfileEnabled">
              {{ editingProfileEnabled ? "Yes" : "No" }}
            </b-checkbox>
          </b-field>

        </b-field>

      </div>
    </div>
  </b-modal>

  <br />

  <h3 class="is-size-3">Misc.</h3>

  <b-field grouped>
    <b-field label="Restart Command"
             message="This will run as '${system_user}' system user - please configure sudoers as needed.  Typical command is like:  sudo supervisorctl restart poser:poser_datasync"
             expanded>
      <b-input name="restart_command"
               v-model="restartCommand"
               @input="settingsNeedSaved = true">
      </b-input>
    </b-field>
  </b-field>

</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.showConfigFilesNote = false
    ThisPageData.profilesData = ${json.dumps(profiles_data)|n}
    ThisPageData.showDisabledProfiles = false

    ThisPageData.editProfileShowDialog = false
    ThisPageData.editingProfile = null
    ThisPageData.editingProfileKey = null
    ThisPageData.editingProfileWatcherSpec = null
    ThisPageData.editingProfileWatcherDBKey = null
    ThisPageData.editingProfileWatcherDelay = 1
    ThisPageData.editingProfileWatcherRetryAttempts = 1
    ThisPageData.editingProfileWatcherRetryDelay = 1
    ThisPageData.editingProfileWatcherDefaultRunas = null
    ThisPageData.editingProfileWatcherConsumesSelf = false
    ThisPageData.editingProfilePendingConsumers = []
    ThisPageData.editingProfileEnabled = true

    ThisPageData.editingConsumer = null
    ThisPageData.editingConsumerKey = null
    ThisPageData.editingConsumerSpec = null
    ThisPageData.editingConsumerDBKey = null
    ThisPageData.editingConsumerDelay = 1
    ThisPageData.editingConsumerRetryAttempts = 1
    ThisPageData.editingConsumerRetryDelay = 1
    ThisPageData.editingConsumerRunas = null
    ThisPageData.editingConsumerEnabled = true

    ThisPageData.restartCommand = ${json.dumps(restart_command)|n}

    ThisPage.computed.filteredProfilesData = function() {
        if (this.showDisabledProfiles) {
            return this.profilesData
        }
        let data = []
        for (let row of this.profilesData) {
            if (row.enabled) {
                data.push(row)
            }
        }
        return data
    }

    ThisPage.computed.updateConsumerDisabled = function() {
        if (!this.editingConsumerKey) {
            return true
        }
        if (!this.editingConsumerSpec) {
            return true
        }
        return false
    }

    ThisPage.computed.updateProfileDisabled = function() {
        if (this.editingConsumer) {
            return true
        }
        if (!this.editingProfileKey) {
            return true
        }
        if (!this.editingProfileWatcherSpec) {
            return true
        }
        return false
    }

    ThisPage.methods.toggleDisabledProfiles = function() {
        this.showDisabledProfiles = !this.showDisabledProfiles
    }

    ThisPage.methods.consumerShortList = function(row) {
        let keys = []
        if (row.watcher_consumes_self) {
            keys.push('self (watcher)')
        } else {
            for (let consumer of row.consumers_data) {
                if (consumer.enabled) {
                    keys.push(consumer.key)
                }
            }
        }
        return keys.join(', ')
    }

    ThisPage.methods.newProfile = function() {
        this.editingProfile = {}
        this.editingConsumer = null

        this.editingProfileKey = null
        this.editingProfileWatcherSpec = null
        this.editingProfileWatcherDBKey = null
        this.editingProfileWatcherDelay = 1
        this.editingProfileWatcherRetryAttempts = 1
        this.editingProfileWatcherRetryDelay = 1
        this.editingProfileWatcherDefaultRunas = null
        this.editingProfileWatcherConsumesSelf = false
        this.editingProfileEnabled = true
        this.editingProfilePendingConsumers = []

        this.editProfileShowDialog = true
        this.$nextTick(() => {
            this.$refs.watcherKeyInput.focus()
        })
    }

    ThisPage.methods.editProfile = function(row) {
        this.editingProfile = row
        this.editingConsumer = null

        this.editingProfileKey = row.key
        this.editingProfileWatcherSpec = row.watcher_spec
        this.editingProfileWatcherDBKey = row.watcher_dbkey
        this.editingProfileWatcherDelay = row.watcher_delay
        this.editingProfileWatcherRetryAttempts = row.watcher_retry_attempts
        this.editingProfileWatcherRetryDelay = row.watcher_retry_delay
        this.editingProfileWatcherDefaultRunas = row.watcher_default_runas
        this.editingProfileWatcherConsumesSelf = row.watcher_consumes_self
        this.editingProfileEnabled = row.enabled

        this.editingProfilePendingConsumers = []
        for (let consumer of row.consumers_data) {
            let pending = {
                original_key: consumer.key,
                key: consumer.key,
                consumer_spec: consumer.consumer_spec,
                consumer_dbkey: consumer.consumer_dbkey,
                consumer_delay: consumer.consumer_delay,
                consumer_retry_attempts: consumer.consumer_retry_attempts,
                consumer_retry_delay: consumer.consumer_retry_delay,
                consumer_runas: consumer.consumer_runas,
                enabled: consumer.enabled,
            }
            this.editingProfilePendingConsumers.push(pending)
        }

        this.editProfileShowDialog = true
    }

    ThisPage.methods.findOriginalConsumer = function(key) {
        for (let consumer of this.editingProfile.consumers_data) {
            if (consumer.key == key) {
                return consumer
            }
        }
    }

    ThisPage.methods.updateProfile = function() {
        let row = this.editingProfile

        if (!row.key) {
            row.consumers_data = []
            this.profilesData.push(row)
        }

        row.key = this.editingProfileKey
        row.watcher_spec = this.editingProfileWatcherSpec
        row.watcher_dbkey = this.editingProfileWatcherDBKey
        row.watcher_delay = this.editingProfileWatcherDelay
        row.watcher_retry_attempts = this.editingProfileWatcherRetryAttempts
        row.watcher_retry_delay = this.editingProfileWatcherRetryDelay
        row.watcher_default_runas = this.editingProfileWatcherDefaultRunas
        row.watcher_consumes_self = this.editingProfileWatcherConsumesSelf
        row.enabled = this.editingProfileEnabled

        // track which keys still belong (persistent)
        let persistent = []

        // transfer pending data to profile consumers
        for (let pending of this.editingProfilePendingConsumers) {
            persistent.push(pending.key)
            if (pending.original_key) {
                let consumer = this.findOriginalConsumer(pending.original_key)
                consumer.key = pending.key
                consumer.consumer_spec = pending.consumer_spec
                consumer.consumer_dbkey = pending.consumer_dbkey
                consumer.consumer_delay = pending.consumer_delay
                consumer.consumer_retry_attempts = pending.consumer_retry_attempts
                consumer.consumer_retry_delay = pending.consumer_retry_delay
                consumer.consumer_runas = pending.consumer_runas
                consumer.enabled = pending.enabled
            } else {
                row.consumers_data.push(pending)
            }
        }

        // remove any consumers not being persisted
        let remove = []
        for (let consumer of row.consumers_data) {
            let i = persistent.indexOf(consumer.key)
            if (i < 0) {
                remove.push(consumer)
            }
        }
        for (let consumer of remove) {
            let i = row.consumers_data.indexOf(consumer)
            row.consumers_data.splice(i, 1)
        }

        this.settingsNeedSaved = true
        this.editProfileShowDialog = false
    }

    ThisPage.methods.deleteProfile = function(row) {
        if (confirm("Are you sure you want to delete the '" + row.key + "' profile?")) {
            let i = this.profilesData.indexOf(row)
            this.profilesData.splice(i, 1)
            this.settingsNeedSaved = true
        }
    }

    ThisPage.methods.newConsumer = function() {
        this.editingConsumerKey = null
        this.editingConsumerSpec = null
        this.editingConsumerDBKey = null
        this.editingConsumerDelay = 1
        this.editingConsumerRetryAttempts = 1
        this.editingConsumerRetryDelay = 1
        this.editingConsumerRunas = null
        this.editingConsumerEnabled = true
        this.editingConsumer = {}
        this.$nextTick(() => {
            this.$refs.consumerKeyInput.focus()
        })
    }

    ThisPage.methods.editProfileConsumer = function(row) {
        this.editingConsumerKey = row.key
        this.editingConsumerSpec = row.consumer_spec
        this.editingConsumerDBKey = row.consumer_dbkey
        this.editingConsumerDelay = row.consumer_delay
        this.editingConsumerRetryAttempts = row.consumer_retry_attempts
        this.editingConsumerRetryDelay = row.consumer_retry_delay
        this.editingConsumerRunas = row.consumer_runas
        this.editingConsumerEnabled = row.enabled
        this.editingConsumer = row
    }

    ThisPage.methods.updateConsumer = function() {
        let pending = this.editingConsumer
        let isNew = !pending.key

        pending.key = this.editingConsumerKey
        pending.consumer_spec = this.editingConsumerSpec
        pending.consumer_dbkey = this.editingConsumerDBKey
        pending.consumer_delay = this.editingConsumerDelay
        pending.consumer_retry_attempts = this.editingConsumerRetryAttempts
        pending.consumer_retry_delay = this.editingConsumerRetryDelay
        pending.consumer_runas = this.editingConsumerRunas
        pending.enabled = this.editingConsumerEnabled

        if (isNew) {
            this.editingProfilePendingConsumers.push(pending)
        }
        this.editingConsumer = null
    }

    ThisPage.methods.deleteProfileConsumer = function(row) {
        if (confirm("Are you sure you want to delete the '" + row.key + "' consumer?")) {
            let i = this.editingProfilePendingConsumers.indexOf(row)
            this.editingProfilePendingConsumers.splice(i, 1)
        }
    }

    % if request.has_perm('datasync.restart'):
        ThisPageData.restartingDatasync = false
        ThisPageData.restartDatasyncFormButtonText = "Restart Datasync"
        ThisPage.methods.restartDatasync = function(e) {
            if (this.settingsNeedSaved) {
                alert("You have unsaved changes.  Please save or undo them first.")
                e.preventDefault()
            }
        }
        ThisPage.methods.submitRestartDatasyncForm = function() {
            this.restartingDatasync = true
            this.restartDatasyncFormButtonText = "Restarting Datasync..."
        }
    % endif

  </script>
</%def>


${parent.body()}
