## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">App Settings</%def>

<%def name="content_title()"></%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.appsettings.js') + '?ver={}'.format(tailbone.__version__))}
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if not use_buefy:
  <style type="text/css">
    div.form {
        float: none;
    }
    div.panel {
        width: 85%;
    }
    .field-wrapper {
        margin-bottom: 2em;
    }
    .panel .field-wrapper label {
        font-family: monospace;
        width: 50em;
    }
  </style>
  % endif
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('settings.list'):
      <li>${h.link_to("View Raw Settings", url('settings'))}</li>
  % endif
</%def>

<%def name="page_content()">
  <app-settings :groups="groups" :showing-group="showingGroup"></app-settings>
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  <script type="text/x-template" id="app-settings-template">

    <div class="form">
      ${h.form(form.action_url, id=dform.formid, method='post', **{'@submit': 'submitForm'})}
      ${h.csrf_token(request)}

      % if dform.error:
          <b-notification type="is-warning">
            Please see errors below.
          </b-notification>
          <b-notification type="is-warning">
            ${dform.error}
          </b-notification>
      % endif

      <div class="app-wrapper">

        <div class="level">

          <div class="level-left">
            <div class="level-item">
              <b-field label="Showing Group">
                <b-select name="settings-group"
                          v-model="showingGroup">
                  <option value="">(All)</option>
                  <option v-for="group in groups"
                          :key="group.label"
                          :value="group.label">
                    {{ group.label }}
                  </option>
                </b-select>
              </b-field>
            </div>
          </div>

          <div class="level-right"
               v-if="configOptions.length">
            <div class="level-item">
              <b-field label="Go To Configure...">
                <b-select v-model="gotoConfigureURL"
                          @input="gotoConfigure()">
                  <option v-for="option in configOptions"
                          :key="option.url"
                          :value="option.url">
                    {{ option.label }}
                  </option>
                </b-select>
              </b-field>
            </div>
          </div>

        </div>

        <div v-for="group in groups"
             class="card"
             v-show="!showingGroup || showingGroup == group.label"
             style="margin-bottom: 1rem;">
          <header class="card-header">
            <p class="card-header-title">{{ group.label }}</p>
          </header>
          <div class="card-content">
            <div v-for="setting in group.settings"
                 ## TODO: not sure how the error handling looks now?
                 ## :class="'field-wrapper' + (setting.error ? ' with-error' : '')"
                 >

              <div style="margin-bottom: 2rem;">

                <b-field horizontal
                         :label="setting.label"
                         :type="setting.error ? 'is-danger' : null"
                         ## TODO: what if there are multiple error messages?
                         :message="setting.error ? setting.error_messages[0] : null">

                  <b-checkbox v-if="setting.data_type == 'bool'"
                              :name="setting.field_name"
                              :id="setting.field_name"
                              v-model="setting.value"
                              native-value="true">
                    {{ setting.value || false }}
                  </b-checkbox>

                  <b-input v-else-if="setting.data_type == 'list'"
                           type="textarea"
                           :name="setting.field_name"
                           v-model="setting.value">
                  </b-input>

                  <b-select v-else-if="setting.choices"
                            :name="setting.field_name"
                            :id="setting.field_name"
                            v-model="setting.value">
                    <option v-for="choice in setting.choices"
                            :value="choice">
                      {{ choice }}
                    </option>
                  </b-select>

                  <b-input v-else
                           :name="setting.field_name"
                           :id="setting.field_name"
                           v-model="setting.value" />

                </b-field>

                <span v-if="setting.helptext"
                      v-html="setting.helptext"
                      class="instructions">
                </span>
              </div>

            </div>
          </div><!-- card-content -->
        </div><!-- card -->

        <div class="buttons">
          <once-button tag="a" href="${form.cancel_url}"
                       text="Cancel">
          </once-button>
          <b-button type="is-primary"
                    native-type="submit"
                    :disabled="formSubmitting">
            {{ formButtonText }}
          </b-button>
        </div>

      </div><!-- app-wrapper -->

      ${h.end_form()}
    </div>
  </script>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.groups = ${json.dumps(buefy_data)|n}
    ThisPageData.showingGroup = ${json.dumps(current_group or '')|n}

  </script>
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  <script type="text/javascript">

    Vue.component('app-settings', {
        template: '#app-settings-template',
        props: {
            groups: Array,
            showingGroup: String
        },
        data() {
            return {
                formSubmitting: false,
                formButtonText: ${json.dumps(getattr(form, 'submit_label', getattr(form, 'save_label', "Submit")))|n},
                configOptions: ${json.dumps(config_options)|n},
                gotoConfigureURL: null,
            }
        },
        methods: {
            submitForm() {
                this.formSubmitting = true
                this.formButtonText = "Working, please wait..."
            },
            gotoConfigure() {
                if (this.gotoConfigureURL) {
                    location.href = this.gotoConfigureURL
                }
            },
        }
    })

  </script>
</%def>


% if use_buefy:
    ${parent.body()}

% else:
## legacy / not buefy
<div class="form">
  ${h.form(form.action_url, id=dform.formid, method='post', class_='autodisable')}
  ${h.csrf_token(request)}

  % if dform.error:
      <div class="error-messages">
        <div class="ui-state-error ui-corner-all">
          <span style="float: left; margin-right: .3em;" class="ui-icon ui-icon-alert"></span>
          Please see errors below.
        </div>
        <div class="ui-state-error ui-corner-all">
          <span style="float: left; margin-right: .3em;" class="ui-icon ui-icon-alert"></span>
          ${dform.error}
        </div>
      </div>
  % endif

  <div class="group-picker">
    <div class="field-wrapper">
      <label for="settings-group">Showing Group</label>
      <div class="field select">
        ${h.select('settings-group', current_group, group_options, **{'auto-enhance': 'true'})}
      </div>
    </div>
  </div>

  % for group in groups:
      <div class="panel" data-groupname="${group}">
        <h2>${group}</h2>
        <div class="panel-body">

          % for setting in settings:
              % if setting.group == group:
                  <% field = dform[setting.node_name] %>

                  <div class="field-wrapper ${field.name} ${'with-error' if field.error else ''}">
                    % if field.error:
                        <div class="field-error">
                          % for msg in field.error.messages():
                              <span class="error-msg">${msg}</span>
                          % endfor
                        </div>
                    % endif
                    <div class="field-row">
                      <label for="${field.oid}">${form.get_label(field.name)}</label>
                      <div class="field">
                        ${field.serialize()|n}
                      </div>
                    </div>
                    % if form.has_helptext(field.name):
                        <span class="instructions">${form.render_helptext(field.name)}</span>
                    % endif
                  </div>
              % endif
          % endfor

        </div><!-- panel-body -->
      </div><! -- panel -->
  % endfor

  <div class="buttons">
    ${h.submit('save', getattr(form, 'submit_label', getattr(form, 'save_label', "Submit")), class_='button is-primary')}
    ${h.link_to("Cancel", form.cancel_url, class_='cancel button{}'.format(' autodisable' if form.auto_disable_cancel else ''))}
  </div>

  ${h.end_form()}
</div>
% endif
