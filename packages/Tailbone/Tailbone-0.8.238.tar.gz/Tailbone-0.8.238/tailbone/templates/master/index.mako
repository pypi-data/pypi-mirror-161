## -*- coding: utf-8; -*-
## ##############################################################################
## 
## Default master 'index' template.  Features a prominent data table and
## exposes a way to filter and sort the data, etc.  Some index pages also
## include a "tools" section, just above the grid on the right.
## 
## ##############################################################################
<%inherit file="/page.mako" />

<%def name="title()">${index_title}</%def>

<%def name="content_title()"></%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">
    $(function() {

        % if download_results_rows_path:
            function downloadResultsRowsRedirect() {
                location.href = '${url('{}.download_results_rows'.format(route_prefix))}?filename=${h.os.path.basename(download_results_rows_path)}';
            }
            // we give this 1 second before attempting the redirect; so this
            // way the page should fully render before redirecting
            window.setTimeout(downloadResultsRowsRedirect, 1000);
        % endif

        $('.grid-wrapper').gridwrapper();

        % if master.deletable and request.has_perm('{}.delete'.format(permission_prefix)) and master.delete_confirm == 'simple':

            $('.grid-wrapper').on('click', '.grid .actions a.delete', function() {
                if (confirm("Are you sure you wish to delete this ${model_title}?")) {
                    var link = $(this).get(0);
                    var form = $('#delete-object-form').get(0);
                    form.action = link.href;
                    form.submit();
                }
                return false;
            });

        % endif

        % if master.mergeable and master.has_perm('merge'):

            $('form[name="merge-things"] button').button('option', 'disabled', $('.grid').gridcore('count_selected') != 2);

            $('.grid-wrapper').on('gridchecked', '.grid', function(event, count) {
                $('form[name="merge-things"] button').button('option', 'disabled', count != 2);
            });

            $('form[name="merge-things"]').submit(function() {
                var uuids = $('.grid').gridcore('selected_uuids');
                if (uuids.length != 2) {
                    return false;
                }
                $(this).find('[name="uuids"]').val(uuids.toString());
                $(this).find('button')
                    .button('option', 'label', "Preparing to Merge...")
                    .button('disable');
            });

        % endif

        % if master.has_rows and master.results_rows_downloadable:

            $('#download-row-results-button').click(function() {
                if (confirm("This will generate an Excel file which contains "
                            + "not the results themselves, but the *rows* for "
                            + "each.\n\nAre you sure you want this?")) {
                    disable_button(this);
                    var form = $(this).parents('form');
                    form.submit();
                }
            });

        % endif

        % if master.bulk_deletable and request.has_perm('{}.bulk_delete'.format(permission_prefix)):

        $('form[name="bulk-delete"] button').click(function() {
            var count = $('.grid-wrapper').gridwrapper('results_count', true);
            if (count === null) {
                alert("There don't seem to be any results to delete!");
                return;
            }
            if (! confirm("You are about to delete " + count + " ${model_title_plural}.\n\nAre you sure?")) {
                return
            }
            $(this).button('disable').button('option', 'label', "Deleting Results...");
            $('form[name="bulk-delete"]').submit();
        });

        % endif

        % if master.supports_set_enabled_toggle and request.has_perm('{}.enable_disable_set'.format(permission_prefix)):
            $('form[name="enable-set"] button').click(function() {
                var form = $(this).parents('form');
                var uuids = $('.grid').gridcore('selected_uuids');
                if (! uuids.length) {
                    alert("You must first select one or more objects to enable.");
                    return false;
                }
                if (! confirm("Are you sure you wish to ENABLE the " + uuids.length + " selected objects?")) {
                    return false;
                }
                form.find('[name="uuids"]').val(uuids.toString());
                disable_button(this);
                form.submit();
            });

            $('form[name="disable-set"] button').click(function() {
                var form = $(this).parents('form');
                var uuids = $('.grid').gridcore('selected_uuids');
                if (! uuids.length) {
                    alert("You must first select one or more objects to disable.");
                    return false;
                }
                if (! confirm("Are you sure you wish to DISABLE the " + uuids.length + " selected objects?")) {
                    return false;
                }
                form.find('[name="uuids"]').val(uuids.toString());
                disable_button(this);
                form.submit();
            });
        % endif

        % if master.set_deletable and request.has_perm('{}.delete_set'.format(permission_prefix)):
            $('form[name="delete-set"] button').click(function() {
                var form = $(this).parents('form');
                var uuids = $('.grid').gridcore('selected_uuids');
                if (! uuids.length) {
                    alert("You must first select one or more objects to delete.");
                    return false;
                }
                if (! confirm("Are you sure you wish to DELETE the " + uuids.length + " selected objects?")) {
                    return false;
                }
                form.find('[name="uuids"]').val(uuids.toString());
                disable_button(this);
                form.submit();
            });
        % endif
    });
  </script>
  % endif
</%def>

<%def name="context_menu_items()">
  % if master.results_downloadable_csv and request.has_perm('{}.results_csv'.format(permission_prefix)):
      <li>${h.link_to("Download results as CSV", url('{}.results_csv'.format(route_prefix)))}</li>
  % endif
  % if master.results_downloadable_xlsx and request.has_perm('{}.results_xlsx'.format(permission_prefix)):
      <li>${h.link_to("Download results as XLSX", url('{}.results_xlsx'.format(route_prefix)))}</li>
  % endif
  % if not use_buefy and master.creatable and master.show_create_link and master.has_perm('create'):
      % if master.creates_multiple:
          <li>${h.link_to("Create new {}".format(model_title_plural), url('{}.create'.format(route_prefix)))}</li>
      % else:
          <li>${h.link_to("Create a new {}".format(model_title), url('{}.create'.format(route_prefix)))}</li>
      % endif
  % endif
  % if master.has_input_file_templates and master.has_perm('create'):
      % for template in six.itervalues(input_file_templates):
          <li>${h.link_to("Download {} Template".format(template['label']), template['effective_url'])}</li>
      % endfor
  % endif
</%def>

<%def name="grid_tools()">

  ## download search results
  % if master.results_downloadable and master.has_perm('download_results'):
      % if use_buefy:
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="fas fa-download"
                    @click="showDownloadResultsDialog = true"
                    :disabled="!total">
            Download Results
          </b-button>

          ${h.form(url('{}.download_results'.format(route_prefix)), ref='download_results_form')}
          ${h.csrf_token(request)}
          <input type="hidden" name="fmt" :value="downloadResultsFormat" />
          <input type="hidden" name="fields" :value="downloadResultsFieldsIncluded" />
          ${h.end_form()}

          <b-modal :active.sync="showDownloadResultsDialog">
            <div class="card">

              <div class="card-content">
                <p>
                  There are
                  <span class="is-size-4 has-text-weight-bold">
                    {{ total.toLocaleString('en') }} ${model_title_plural}
                  </span>
                  matching your current filters.
                </p>
                <p>
                  You may download this set as a single data file if you like.
                </p>
                <br />

                <b-notification type="is-warning" :closable="false"
                                v-if="downloadResultsFormat == 'xlsx' && total >= 1000">
                  Excel downloads for large data sets can take a long time to
                  generate, and bog down the server in the meantime.  You are
                  encouraged to choose CSV for a large data set, even though
                  the end result (file size) may be larger with CSV.
                </b-notification>

                <div style="display: flex; justify-content: space-between">

                  <div>
                    <b-field horizontal label="Format">
                      <b-select v-model="downloadResultsFormat">
                        % for key, label in six.iteritems(master.download_results_supported_formats()):
                        <option value="${key}">${label}</option>
                        % endfor
                      </b-select>
                    </b-field>
                  </div>

                  <div>

                    <div v-show="downloadResultsFieldsMode != 'choose'"
                         class="has-text-right">
                      <p v-if="downloadResultsFieldsMode == 'default'">
                        Will use DEFAULT fields.
                      </p>
                      <p v-if="downloadResultsFieldsMode == 'all'">
                        Will use ALL fields.
                      </p>
                      <br />
                    </div>

                    <div class="buttons is-right">
                      <b-button type="is-primary"
                                v-show="downloadResultsFieldsMode != 'default'"
                                @click="downloadResultsUseDefaultFields()">
                        Use Default Fields
                      </b-button>
                      <b-button type="is-primary"
                                v-show="downloadResultsFieldsMode != 'all'"
                                @click="downloadResultsUseAllFields()">
                        Use All Fields
                      </b-button>
                      <b-button type="is-primary"
                                v-show="downloadResultsFieldsMode != 'choose'"
                                @click="downloadResultsFieldsMode = 'choose'">
                        Choose Fields
                      </b-button>
                    </div>

                    <div v-show="downloadResultsFieldsMode == 'choose'">
                      <div style="display: flex;">
                        <div>
                          <b-field label="Excluded Fields">
                            <b-select multiple native-size="8"
                                      expanded
                                      ref="downloadResultsExcludedFields">
                              <option v-for="field in downloadResultsFieldsAvailable"
                                      v-if="!downloadResultsFieldsIncluded.includes(field)"
                                      :key="field"
                                      :value="field">
                                {{ field }}
                              </option>
                            </b-select>
                          </b-field>
                        </div>
                        <div>
                          <br /><br />
                          <b-button style="margin: 0.5rem;"
                                    @click="downloadResultsExcludeFields()">
                            &lt;
                          </b-button>
                          <br />
                          <b-button style="margin: 0.5rem;"
                                    @click="downloadResultsIncludeFields()">
                            &gt;
                          </b-button>
                        </div>
                        <div>
                          <b-field label="Included Fields">
                            <b-select multiple native-size="8"
                                      expanded
                                      ref="downloadResultsIncludedFields">
                              <option v-for="field in downloadResultsFieldsIncluded"
                                      :key="field"
                                      :value="field">
                                {{ field }}
                              </option>
                            </b-select>
                          </b-field>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div> <!-- card-content -->

              <footer class="modal-card-foot">
                <b-button @click="showDownloadResultsDialog = false">
                  Cancel
                </b-button>
                <once-button type="is-primary"
                             @click="downloadResultsSubmit()"
                             icon-pack="fas"
                             icon-left="fas fa-download"
                             :disabled="!downloadResultsFieldsIncluded.length"
                             text="Download Results">
                </once-button>
              </footer>
            </div>
          </b-modal>
      % endif
  % endif

  ## download rows for search results
  % if master.has_rows and master.results_rows_downloadable and master.has_perm('download_results_rows'):
      % if use_buefy:
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="fas fa-download"
                    @click="downloadResultsRows()"
                    :disabled="downloadResultsRowsButtonDisabled">
            {{ downloadResultsRowsButtonText }}
          </b-button>
          ${h.form(url('{}.download_results_rows'.format(route_prefix)), ref='downloadResultsRowsForm')}
          ${h.csrf_token(request)}
          ${h.end_form()}
      % else:
          ${h.form(url('{}.download_results_rows'.format(route_prefix)))}
          ${h.csrf_token(request)}
          <button type="button" id="download-row-results-button">
            Download Rows for Results
          </button>
          ${h.end_form()}
      % endif
  % endif

  ## merge 2 objects
  % if master.mergeable and request.has_perm('{}.merge'.format(permission_prefix)):

      % if use_buefy:
      ${h.form(url('{}.merge'.format(route_prefix)), class_='control', **{'@submit': 'submitMergeForm'})}
      % else:
      ${h.form(url('{}.merge'.format(route_prefix)), name='merge-things')}
      % endif
      ${h.csrf_token(request)}
      % if use_buefy:
          <input type="hidden"
                 name="uuids"
                 :value="checkedRowUUIDs()" />
          <b-button type="is-primary"
                    native-type="submit"
                    icon-pack="fas"
                    icon-left="object-ungroup"
                    :disabled="mergeFormSubmitting || checkedRows.length != 2">
            {{ mergeFormButtonText }}
          </b-button>
      % else:
          ${h.hidden('uuids')}
          <button type="submit" class="button">Merge 2 ${model_title_plural}</button>
      % endif
      ${h.end_form()}
  % endif

  ## enable / disable selected objects
  % if master.supports_set_enabled_toggle and master.has_perm('enable_disable_set'):

      % if use_buefy:
          ${h.form(url('{}.enable_set'.format(route_prefix)), class_='control', ref='enable_selected_form')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids', v_model='selected_uuids')}
          <b-button :disabled="enableSelectedDisabled"
                    @click="enableSelectedSubmit()">
            {{ enableSelectedText }}
          </b-button>
          ${h.end_form()}
      % else:
          ${h.form(url('{}.enable_set'.format(route_prefix)), name='enable-set', class_='control')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids')}
          <button type="button" class="button">Enable Selected</button>
          ${h.end_form()}
      % endif

      % if use_buefy:
          ${h.form(url('{}.disable_set'.format(route_prefix)), ref='disable_selected_form', class_='control')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids', v_model='selected_uuids')}
          <b-button :disabled="disableSelectedDisabled"
                    @click="disableSelectedSubmit()">
            {{ disableSelectedText }}
          </b-button>
          ${h.end_form()}
      % else:
          ${h.form(url('{}.disable_set'.format(route_prefix)), name='disable-set', class_='control')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids')}
          <button type="button" class="button">Disable Selected</button>
          ${h.end_form()}
      % endif
  % endif

  ## delete selected objects
  % if master.set_deletable and master.has_perm('delete_set'):
      % if use_buefy:
          ${h.form(url('{}.delete_set'.format(route_prefix)), ref='delete_selected_form', class_='control')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids', v_model='selected_uuids')}
          <b-button type="is-danger"
                    :disabled="deleteSelectedDisabled"
                    @click="deleteSelectedSubmit()"
                    icon-pack="fas"
                    icon-left="trash">
            {{ deleteSelectedText }}
          </b-button>
          ${h.end_form()}
      % else:
          ${h.form(url('{}.delete_set'.format(route_prefix)), name='delete-set', class_='control')}
          ${h.csrf_token(request)}
          ${h.hidden('uuids')}
          <button type="button" class="button">Delete Selected</button>
          ${h.end_form()}
      % endif
  % endif

  ## delete search results
  % if master.bulk_deletable and request.has_perm('{}.bulk_delete'.format(permission_prefix)):
      % if use_buefy:
          ${h.form(url('{}.bulk_delete'.format(route_prefix)), ref='delete_results_form', class_='control')}
          ${h.csrf_token(request)}
          <b-button type="is-danger"
                    :disabled="deleteResultsDisabled"
                    :title="total ? null : 'There are no results to delete'"
                    @click="deleteResultsSubmit()"
                    icon-pack="fas"
                    icon-left="trash">
            {{ deleteResultsText }}
          </b-button>
          ${h.end_form()}
      % else:
          ${h.form(url('{}.bulk_delete'.format(route_prefix)), name='bulk-delete', class_='control')}
          ${h.csrf_token(request)}
          <button type="button">Delete Results</button>
          ${h.end_form()}
      % endif
  % endif

</%def>

<%def name="page_content()">

  % if download_results_path:
      <b-notification type="is-info">
        Your download should start automatically, or you can
        ${h.link_to("click here", '{}?filename={}'.format(url('{}.download_results'.format(route_prefix)), h.os.path.basename(download_results_path)))}
      </b-notification>
  % endif

  % if download_results_rows_path:
      <b-notification type="is-info">
        Your download should start automatically, or you can
        ${h.link_to("click here", '{}?filename={}'.format(url('{}.download_results_rows'.format(route_prefix)), h.os.path.basename(download_results_rows_path)))}
      </b-notification>
  % endif

  ${self.render_grid_component()}

  % if master.deletable and request.has_perm('{}.delete'.format(permission_prefix)) and master.delete_confirm == 'simple':
      ${h.form('#', ref='deleteObjectForm')}
      ${h.csrf_token(request)}
      ${h.end_form()}
  % endif
</%def>

<%def name="render_grid_component()">
  <${grid.component} :csrftoken="csrftoken"
     % if master.deletable and request.has_perm('{}.delete'.format(permission_prefix)) and master.delete_confirm == 'simple':
     @deleteActionClicked="deleteObject"
     % endif
     >
  </${grid.component}>
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  <script type="text/javascript">

    ${grid.component_studly}.data = function() { return ${grid.component_studly}Data }

    Vue.component('${grid.component}', ${grid.component_studly})

  </script>
</%def>

<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}

  ## TODO: stop using |n filter
  ${grid.render_buefy(tools=capture(self.grid_tools).strip(), context_menu=capture(self.context_menu_items).strip())|n}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ## maybe auto-redirect to download latest results file
    % if download_results_path and use_buefy:
        ThisPage.methods.downloadResultsRedirect = function() {
            location.href = '${url('{}.download_results'.format(route_prefix))}?filename=${h.os.path.basename(download_results_path)}';
        }
        ThisPage.mounted = function() {
            // we give this 1 second before attempting the redirect; otherwise
            // the FontAwesome icons do not seem to load properly.  so this way
            // the page should fully render before redirecting
            window.setTimeout(this.downloadResultsRedirect, 1000)
        }
    % endif

    ## maybe auto-redirect to download latest "rows for results" file
    % if download_results_rows_path and use_buefy:
        ThisPage.methods.downloadResultsRowsRedirect = function() {
            location.href = '${url('{}.download_results_rows'.format(route_prefix))}?filename=${h.os.path.basename(download_results_rows_path)}';
        }
        ThisPage.mounted = function() {
            // we give this 1 second before attempting the redirect; otherwise
            // the FontAwesome icons do not seem to load properly.  so this way
            // the page should fully render before redirecting
            window.setTimeout(this.downloadResultsRowsRedirect, 1000)
        }
    % endif

    ## TODO: stop checking for buefy here once we only have the one session.pop()
    % if use_buefy and request.session.pop('{}.results_csv.generated'.format(route_prefix), False):
        ThisPage.mounted = function() {
            location.href = '${url('{}.results_csv_download'.format(route_prefix))}';
        }
    % endif
    % if use_buefy and request.session.pop('{}.results_xlsx.generated'.format(route_prefix), False):
        ThisPage.mounted = function() {
            location.href = '${url('{}.results_xlsx_download'.format(route_prefix))}';
        }
    % endif

    ## delete single object
    % if master.deletable and master.has_perm('delete') and master.delete_confirm == 'simple':
        ThisPage.methods.deleteObject = function(url) {
            if (confirm("Are you sure you wish to delete this ${model_title}?")) {
                let form = this.$refs.deleteObjectForm
                form.action = url
                form.submit()
            }
        }
    % endif

    ## download results
    % if master.results_downloadable and master.has_perm('download_results'):

        ${grid.component_studly}Data.downloadResultsFormat = '${master.download_results_default_format()}'
        ${grid.component_studly}Data.showDownloadResultsDialog = false
        ${grid.component_studly}Data.downloadResultsFieldsMode = 'default'
        ${grid.component_studly}Data.downloadResultsFieldsAvailable = ${json.dumps(download_results_fields_available)|n}
        ${grid.component_studly}Data.downloadResultsFieldsDefault = ${json.dumps(download_results_fields_default)|n}
        ${grid.component_studly}Data.downloadResultsFieldsIncluded = ${json.dumps(download_results_fields_default)|n}

        ${grid.component_studly}.computed.downloadResultsFieldsExcluded = function() {
            let excluded = []
            this.downloadResultsFieldsAvailable.forEach(field => {
                if (!this.downloadResultsFieldsIncluded.includes(field)) {
                    excluded.push(field)
                }
            }, this)
            return excluded
        }

        ${grid.component_studly}.methods.downloadResultsExcludeFields = function() {
            let selected = this.$refs.downloadResultsIncludedFields.selected
            if (!selected) {
                return
            }
            selected = Array.from(selected)
            selected.forEach(field => {

                // de-select the entry within "included" field input
                let index = this.$refs.downloadResultsIncludedFields.selected.indexOf(field)
                if (index > -1) {
                    this.$refs.downloadResultsIncludedFields.selected.splice(index, 1)
                }

                // remove field from official "included" list
                index = this.downloadResultsFieldsIncluded.indexOf(field)
                if (index > -1) {
                    this.downloadResultsFieldsIncluded.splice(index, 1)
                }
            }, this)
        }

        ${grid.component_studly}.methods.downloadResultsIncludeFields = function() {
            let selected = this.$refs.downloadResultsExcludedFields.selected
            if (!selected) {
                return
            }
            selected = Array.from(selected)
            selected.forEach(field => {

                // de-select the entry within "excluded" field input
                let index = this.$refs.downloadResultsExcludedFields.selected.indexOf(field)
                if (index > -1) {
                    this.$refs.downloadResultsExcludedFields.selected.splice(index, 1)
                }

                // add field to official "included" list
                this.downloadResultsFieldsIncluded.push(field)

            }, this)
        }

        ${grid.component_studly}.methods.downloadResultsUseDefaultFields = function() {
            this.downloadResultsFieldsIncluded = Array.from(this.downloadResultsFieldsDefault)
            this.downloadResultsFieldsMode = 'default'
        }

        ${grid.component_studly}.methods.downloadResultsUseAllFields = function() {
            this.downloadResultsFieldsIncluded = Array.from(this.downloadResultsFieldsAvailable)
            this.downloadResultsFieldsMode = 'all'
        }

        ${grid.component_studly}.methods.downloadResultsSubmit = function() {
            this.$refs.download_results_form.submit()
        }
    % endif

    ## download rows for results
    % if master.has_rows and master.results_rows_downloadable and master.has_perm('download_results_rows'):

        ${grid.component_studly}Data.downloadResultsRowsButtonDisabled = false
        ${grid.component_studly}Data.downloadResultsRowsButtonText = "Download Rows for Results"

        ${grid.component_studly}.methods.downloadResultsRows = function() {
            if (confirm("This will generate an Excel file which contains "
                        + "not the results themselves, but the *rows* for "
                        + "each.\n\nAre you sure you want this?")) {
                this.downloadResultsRowsButtonDisabled = true
                this.downloadResultsRowsButtonText = "Working, please wait..."
                this.$refs.downloadResultsRowsForm.submit()
            }
        }
    % endif

    ## enable / disable selected objects
    % if master.supports_set_enabled_toggle and master.has_perm('enable_disable_set'):

        ${grid.component_studly}Data.enableSelectedSubmitting = false
        ${grid.component_studly}Data.enableSelectedText = "Enable Selected"

        ${grid.component_studly}.computed.enableSelectedDisabled = function() {
            if (this.enableSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.component_studly}.methods.enableSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to ENABLE the " + uuids.length + " selected objects?")) {
                return
            }

            this.enableSelectedSubmitting = true
            this.enableSelectedText = "Working, please wait..."
            this.$refs.enable_selected_form.submit()
        }

        ${grid.component_studly}Data.disableSelectedSubmitting = false
        ${grid.component_studly}Data.disableSelectedText = "Disable Selected"

        ${grid.component_studly}.computed.disableSelectedDisabled = function() {
            if (this.disableSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.component_studly}.methods.disableSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to DISABLE the " + uuids.length + " selected objects?")) {
                return
            }

            this.disableSelectedSubmitting = true
            this.disableSelectedText = "Working, please wait..."
            this.$refs.disable_selected_form.submit()
        }

    % endif

    ## delete selected objects
    % if master.set_deletable and master.has_perm('delete_set'):

        ${grid.component_studly}Data.deleteSelectedSubmitting = false
        ${grid.component_studly}Data.deleteSelectedText = "Delete Selected"

        ${grid.component_studly}.computed.deleteSelectedDisabled = function() {
            if (this.deleteSelectedSubmitting) {
                return true
            }
            if (!this.checkedRowUUIDs().length) {
                return true
            }
            return false
        }

        ${grid.component_studly}.methods.deleteSelectedSubmit = function() {
            let uuids = this.checkedRowUUIDs()
            if (!uuids.length) {
                alert("You must first select one or more objects to disable.")
                return
            }
            if (! confirm("Are you sure you wish to DELETE the " + uuids.length + " selected objects?")) {
                return
            }

            this.deleteSelectedSubmitting = true
            this.deleteSelectedText = "Working, please wait..."
            this.$refs.delete_selected_form.submit()
        }
    % endif

    % if master.bulk_deletable and master.has_perm('bulk_delete'):

        ${grid.component_studly}Data.deleteResultsSubmitting = false
        ${grid.component_studly}Data.deleteResultsText = "Delete Results"

        ${grid.component_studly}.computed.deleteResultsDisabled = function() {
            if (this.deleteResultsSubmitting) {
                return true
            }
            if (!this.total) {
                return true
            }
            return false
        }

        ${grid.component_studly}.methods.deleteResultsSubmit = function() {
            // TODO: show "plural model title" here?
            if (!confirm("You are about to delete " + this.total.toLocaleString('en') + " objects.\n\nAre you sure?")) {
                return
            }

            this.deleteResultsSubmitting = true
            this.deleteResultsText = "Working, please wait..."
            this.$refs.delete_results_form.submit()
        }

    % endif

    % if master.mergeable and master.has_perm('merge'):

        ${grid.component_studly}Data.mergeFormButtonText = "Merge 2 ${model_title_plural}"
        ${grid.component_studly}Data.mergeFormSubmitting = false

        ${grid.component_studly}.methods.submitMergeForm = function() {
            this.mergeFormSubmitting = true
            this.mergeFormButtonText = "Working, please wait..."
        }
    % endif
  </script>
</%def>


% if use_buefy:
    ${parent.body()}

% else:
    ## no buefy, so do the traditional thing

    % if download_results_rows_path:
        <div class="flash-messages">
          <div class="ui-state-highlight ui-corner-all">
            <span style="float: left; margin-right: .3em;" class="ui-icon ui-icon-info"></span>
            Your download should start automatically, or you can
            ${h.link_to("click here", '{}?filename={}'.format(url('{}.download_results_rows'.format(route_prefix)), h.os.path.basename(download_results_rows_path)))}
          </div>
        </div>
    % endif

    ${grid.render_complete(tools=capture(self.grid_tools).strip(), context_menu=capture(self.context_menu_items).strip())|n}

    % if master.deletable and request.has_perm('{}.delete'.format(permission_prefix)) and master.delete_confirm == 'simple':
        ${h.form('#', id='delete-object-form')}
        ${h.csrf_token(request)}
        ${h.end_form()}
    % endif

    ## TODO: can stop checking for buefy above once this legacy chunk is gone
    % if request.session.pop('{}.results_csv.generated'.format(route_prefix), False):
        <script type="text/javascript">
          $(function() {
              location.href = '${url('{}.results_csv_download'.format(route_prefix))}';
          });
        </script>
    % endif
    % if request.session.pop('{}.results_xlsx.generated'.format(route_prefix), False):
        <script type="text/javascript">
          $(function() {
              location.href = '${url('{}.results_xlsx_download'.format(route_prefix))}';
          });
        </script>
    % endif

% endif
