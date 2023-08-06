## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Configure ${config_title}</%def>

<%def name="save_undo_buttons()">
  <div class="buttons"
       v-if="settingsNeedSaved">
    <b-button type="is-primary"
              @click="saveSettings"
              :disabled="savingSettings"
              icon-pack="fas"
              icon-left="save">
      {{ savingSettings ? "Working, please wait..." : "Save All Settings" }}
    </b-button>
    <once-button tag="a" href="${request.current_route_url()}"
                 @click="undoChanges = true"
                 icon-left="undo"
                 text="Undo All Changes">
    </once-button>
  </div>
</%def>

<%def name="purge_button()">
  <b-button type="is-danger"
            @click="purgeSettingsInit()"
            icon-pack="fas"
            icon-left="trash">
    Remove All Settings
  </b-button>
</%def>

<%def name="intro_message()">
  <p class="block">
    This page lets you modify the
    % if config_preferences is not Undefined and config_preferences:
        preferences
    % else:
        configuration
    % endif
    for ${config_title}.
  </p>
</%def>

<%def name="buttons_row()">
  <div class="level">
    <div class="level-left">

      <div class="level-item">
        ${self.intro_message()}
      </div>

      <div class="level-item">
        ${self.save_undo_buttons()}
      </div>
    </div>

    <div class="level-right">
      <div class="level-item">
        ${self.purge_button()}
      </div>
    </div>
  </div>
</%def>

<%def name="input_file_template_field(key)">
    <% tmpl = input_file_templates[key] %>
    <b-field grouped>

      <b-field label="${tmpl['label']}">
        <b-select name="${tmpl['setting_mode']}"
                  v-model="inputFileTemplateSettings['${tmpl['setting_mode']}']"
                  @input="settingsNeedSaved = true">
          <option value="default">use default</option>
          <option value="hosted">use uploaded file</option>
          <option value="external">use other URL</option>
        </b-select>
      </b-field>

      <b-field label="File"
               v-show="inputFileTemplateSettings['${tmpl['setting_mode']}'] == 'hosted'"
               :message="inputFileTemplateSettings['${tmpl['setting_file']}'] ? 'This file lives on disk at: ${input_file_option_dirs[tmpl['key']]}' : null">
        <b-select name="${tmpl['setting_file']}"
                  v-model="inputFileTemplateSettings['${tmpl['setting_file']}']"
                  @input="settingsNeedSaved = true">
          <option :value="null">-new-</option>
          <option v-for="option in inputFileTemplateFileOptions['${tmpl['key']}']"
                  :key="option"
                  :value="option">
            {{ option }}
          </option>
        </b-select>
      </b-field>

      <b-field label="Upload"
               v-show="inputFileTemplateSettings['${tmpl['setting_mode']}'] == 'hosted' && !inputFileTemplateSettings['${tmpl['setting_file']}']">

        <b-field class="file is-primary"
                 :class="{'has-name': !!inputFileTemplateSettings['${tmpl['setting_file']}']}">
          <b-upload name="${tmpl['setting_file']}.upload"
                    v-model="inputFileTemplateUploads['${tmpl['key']}']"
                    class="file-label"
                    @input="settingsNeedSaved = true">
            <span class="file-cta">
              <b-icon class="file-icon" pack="fas" icon="upload"></b-icon>
              <span class="file-label">Click to upload</span>
            </span>
          </b-upload>
          <span v-if="inputFileTemplateUploads['${tmpl['key']}']"
                class="file-name">
            {{ inputFileTemplateUploads['${tmpl['key']}'].name }}
          </span>
        </b-field>

      </b-field>

      <b-field label="URL" expanded
               v-show="inputFileTemplateSettings['${tmpl['setting_mode']}'] == 'external'">
        <b-input name="${tmpl['setting_url']}"
                 v-model="inputFileTemplateSettings['${tmpl['setting_url']}']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

    </b-field>
</%def>

<%def name="input_file_templates_section()">
  <h3 class="block is-size-3">Input File Templates</h3>
  <div class="block" style="padding-left: 2rem;">
    % for key in input_file_templates:
        ${self.input_file_template_field(key)}
    % endfor
  </div>
</%def>

<%def name="form_content()"></%def>

<%def name="page_content()">
  ${parent.page_content()}

  <br />

  ${self.buttons_row()}

  <b-modal has-modal-card
           :active.sync="purgeSettingsShowDialog">
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Remove All Settings</p>
      </header>

      <section class="modal-card-body">
        <p class="block">
          If you like we can remove all settings for ${config_title}
          from the DB.
        </p>
        <p class="block">
          Note that the tool normally removes all settings first,
          every time you click "Save Settings" - here though you can
          "just remove and not save" the settings.
        </p>
        <p class="block">
          Note also that this will of course 
          <span class="is-italic">not</span> remove any settings from
          your config files, so after removing from DB,
          <span class="is-italic">only</span> your config file
          settings should be in effect.
        </p>
      </section>

      <footer class="modal-card-foot">
        <b-button @click="purgeSettingsShowDialog = false">
          Cancel
        </b-button>
        ${h.form(request.current_route_url())}
        ${h.csrf_token(request)}
        ${h.hidden('remove_settings', 'true')}
        <b-button type="is-danger"
                  native-type="submit"
                  :disabled="purgingSettings"
                  icon-pack="fas"
                  icon-left="trash"
                  @click="purgingSettings = true">
          {{ purgingSettings ? "Working, please wait..." : "Remove All Settings" }}
        </b-button>
        ${h.end_form()}
      </footer>
    </div>
  </b-modal>

  ${h.form(request.current_route_url(), enctype='multipart/form-data', ref='saveSettingsForm', **{'@submit': 'saveSettingsFormSubmit'})}
  ${h.csrf_token(request)}
  ${self.form_content()}
  ${h.end_form()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    % if simple_settings is not Undefined:
        ThisPageData.simpleSettings = ${json.dumps(simple_settings)|n}
    % endif

    % if input_file_template_settings is not Undefined:
        ThisPageData.inputFileTemplateSettings = ${json.dumps(input_file_template_settings)|n}
        ThisPageData.inputFileTemplateFileOptions = ${json.dumps(input_file_options)|n}
        ThisPageData.inputFileTemplateUploads = {
            % for key in input_file_templates:
                '${key}': null,
            % endfor
        }
    % endif

    ThisPageData.purgeSettingsShowDialog = false
    ThisPageData.purgingSettings = false

    ThisPageData.settingsNeedSaved = false
    ThisPageData.undoChanges = false
    ThisPageData.savingSettings = false

    ThisPage.methods.purgeSettingsInit = function() {
        this.purgeSettingsShowDialog = true
    }

    % if input_file_template_settings is not Undefined:
        ThisPage.methods.validateInputFileTemplateSettings = function() {
            % for tmpl in six.itervalues(input_file_templates):
                if (this.inputFileTemplateSettings['${tmpl['setting_mode']}'] == 'hosted') {
                    if (!this.inputFileTemplateSettings['${tmpl['setting_file']}']) {
                        if (!this.inputFileTemplateUploads['${tmpl['key']}']) {
                            return "You must provide a file to upload for the ${tmpl['label']} template."
                        }
                    }
                }
            % endfor
        }
    % endif

    ThisPage.methods.validateSettings = function() {
        let msg

        % if input_file_template_settings is not Undefined:
            msg = this.validateInputFileTemplateSettings()
            if (msg) {
                return msg
            }
        % endif
    }

    ThisPage.methods.saveSettings = function() {
        let msg = this.validateSettings()
        if (msg) {
            alert(msg)
            return
        }

        this.savingSettings = true
        this.settingsNeedSaved = false
        this.$refs.saveSettingsForm.submit()
    }

    // nb. this is here to avoid auto-submitting form when user
    // presses ENTER while some random input field has focus
    ThisPage.methods.saveSettingsFormSubmit = function(event) {
        if (!this.savingSettings) {
            event.preventDefault()
        }
    }

    // cf. https://stackoverflow.com/a/56551646
    ThisPage.methods.beforeWindowUnload = function(e) {
        if (this.settingsNeedSaved && !this.undoChanges) {
            e.preventDefault()
            e.returnValue = ''
        }
    }

    ThisPage.created = function() {
        window.addEventListener('beforeunload', this.beforeWindowUnload)
    }

  </script>
</%def>


${parent.body()}
