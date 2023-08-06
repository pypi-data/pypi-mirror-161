## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.batch.js') + '?ver={}'.format(tailbone.__version__))}
  <script type="text/javascript">

    var has_execution_options = ${'true' if master.has_execution_options(batch) else 'false'};

    $(function() {
        % if master.has_worksheet and master.allow_worksheet(batch) and master.has_perm('worksheet'):
            $('.load-worksheet').click(function() {
                disable_button(this);
                location.href = '${url('{}.worksheet'.format(route_prefix), uuid=batch.uuid)}';
            });
        % endif
        % if master.batch_refreshable(batch) and master.has_perm('refresh'):
            $('#refresh-data').click(function() {
                $(this)
                    .button('option', 'disabled', true)
                    .button('option', 'label', "Working, please wait...");
                location.href = '${url('{}.refresh'.format(route_prefix), uuid=batch.uuid)}';
            });
        % endif
        % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
            $('.upload-worksheet').click(function() {
                $('#upload-worksheet-dialog').dialog({
                    title: "Upload Worksheet",
                    width: 600,
                    modal: true,
                    buttons: [
                        {
                            text: "Upload & Update Batch",
                            click: function(event) {
                                var form = $('form[name="upload-worksheet"]');
                                var field = form.find('input[type="file"]').get(0);
                                if (!field.value) {
                                    alert("Please choose a file to upload.");
                                    return
                                }
                                disable_button(dialog_button(event));
                                form.submit();
                            }
                        },
                        {
                            text: "Cancel",
                            click: function() {
                                $(this).dialog('close');
                            }
                        }
                    ]
                });
            });
        % endif
    });

  </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
  <style type="text/css">

    .modal-card-body label {
        white-space: nowrap;
    }

    .markdown p {
        margin-bottom: 1.5rem;
    }

  </style>
  % else:
  <style type="text/css">

    .grid-wrapper {
        margin-top: 10px;
    }

    .complete form {
        display: inline;
    }
    
  </style>
  % endif
</%def>

<%def name="buttons()">
    <div class="buttons">
      ${self.leading_buttons()}
      ${refresh_button()}
      ${self.trailing_buttons()}
    </div>
</%def>

<%def name="leading_buttons()">
  % if master.has_worksheet and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      % if use_buefy:
          <once-button type="is-primary"
                       tag="a" href="${url('{}.worksheet'.format(route_prefix), uuid=batch.uuid)}"
                       icon-left="edit"
                       text="Edit as Worksheet">
          </once-button>
      % else:
          <button type="button" class="load-worksheet">Edit as Worksheet</button>
      % endif
  % endif
</%def>

<%def name="refresh_button()">
  % if master.batch_refreshable(batch) and master.has_perm('refresh'):
      % if use_buefy:
          ## TODO: this should surely use a POST request?
          <once-button type="is-primary"
                       tag="a" href="${url('{}.refresh'.format(route_prefix), uuid=batch.uuid)}"
                       text="Refresh Data"
                       icon-left="redo">
          </once-button>
      % else:
          <button type="button" class="button" id="refresh-data">Refresh Data</button>
      % endif
  % endif
</%def>

<%def name="trailing_buttons()">
  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      % if use_buefy:
          <b-button tag="a"
                    href="${master.get_action_url('download_worksheet', batch)}"
                    icon-pack="fas"
                    icon-left="fas fa-download">
            Download Worksheet
          </b-button>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="fas fa-upload"
                    @click="$emit('show-upload')">
            Upload Worksheet
          </b-button>
      % else:
          ${h.link_to("Download Worksheet", master.get_action_url('download_worksheet', batch), class_='button')}
          <button type="button" class="upload-worksheet">Upload Worksheet</button>
      % endif
  % endif
</%def>

<%def name="object_helpers()">
  ${self.render_status_breakdown()}
  ${self.render_execute_helper()}
</%def>

<%def name="render_status_breakdown()">
  % if use_buefy:
      <div class="object-helper">
        <h3>Row Status Breakdown</h3>
        <div class="object-helper-content">
          ${status_breakdown_grid}
        </div>
      </div>
  % elif status_breakdown is not Undefined and status_breakdown is not None:
      <div class="object-helper">
        <h3>Row Status Breakdown</h3>
        <div class="object-helper-content">
          % if status_breakdown:
              <div class="grid full">
                <table>
                  % for i, (status, count) in enumerate(status_breakdown):
                      <tr class="${'even' if i % 2 == 0 else 'odd'}">
                        <td>${status}</td>
                        <td>${count}</td>
                      </tr>
                  % endfor
                </table>
              </div>
          % else:
              <p>Nothing to report yet.</p>
          % endif
        </div>
      </div>
  % endif
</%def>

<%def name="render_execute_helper()">
  <div class="object-helper">
    <h3>Batch Execution</h3>
    <div class="object-helper-content">
      % if batch.executed:
          <p>
            Batch was executed
            ${h.pretty_datetime(request.rattail_config, batch.executed)}
            by ${batch.executed_by}
          </p>
      % elif master.handler.executable(batch):
          % if master.has_perm('execute'):
              <p>Batch has not yet been executed.</p>
              % if use_buefy:
                  <br />
                  <b-button type="is-primary"
                            % if not execute_enabled:
                            disabled
                            % if why_not_execute:
                            title="${why_not_execute}"
                            % endif
                            % endif
                            @click="showExecutionDialog = true"
                            icon-pack="fas"
                            icon-left="arrow-circle-right">
                    ${execute_title}
                  </b-button>

                  % if execute_enabled:
                  <b-modal has-modal-card
                           :active.sync="showExecutionDialog">
                    <div class="modal-card">

                      <header class="modal-card-head">
                        <p class="modal-card-title">Execute ${model_title}</p>
                      </header>

                      <section class="modal-card-body">
                        <p class="block has-text-weight-bold">
                          What will happen when this batch is executed?
                        </p>
                        <div class="markdown">
                          ${execution_described|n}
                        </div>
                        <${execute_form.component} ref="executeBatchForm">
                        </${execute_form.component}>
                      </section>

                      <footer class="modal-card-foot">
                        <b-button @click="showExecutionDialog = false">
                          Cancel
                        </b-button>
                        <once-button type="is-primary"
                                     @click="submitExecuteBatch()"
                                     icon-left="arrow-circle-right"
                                     text="Execute Batch">
                        </once-button>
                      </footer>

                    </div>
                  </b-modal>
                  % endif

              % else:
                  ## no buefy, do legacy thing
                  <button type="button"
                          % if not execute_enabled:
                          disabled="disabled"
                          % endif
                          % if why_not_execute:
                          title="${why_not_execute}"
                          % endif
                          class="button is-primary"
                          id="execute-batch">
                    ${execute_title}
                  </button>
              % endif
          % else:
              <p>TODO: batch *may* be executed, but not by *you*</p>
          % endif
      % else:
          <p>TODO: batch cannot be executed..?</p>
      % endif
    </div>
  </div>
</%def>

<%def name="render_form()">
  ## TODO: should use self.render_form_buttons()
  ## ${form.render(form_id='batch-form', buttons=capture(self.render_form_buttons))|n}
  ${form.render(form_id='batch-form', buttons=capture(buttons))|n}
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}

  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      % if use_buefy:
          <b-modal has-modal-card
                   :active.sync="showUploadDialog">
            <div class="modal-card">

              <header class="modal-card-head">
                <p class="modal-card-title">Upload Worksheet</p>
              </header>

              <section class="modal-card-body">
                <p>
                  This will <span class="has-text-weight-bold">update</span>
                  the batch data with the worksheet file you provide.&nbsp;
                  Please be certain to use the right one!
                </p>
                <br />
                <${upload_worksheet_form.component} ref="uploadForm">
                </${upload_worksheet_form.component}>
              </section>

              <footer class="modal-card-foot">
                <b-button @click="showUploadDialog = false">
                  Cancel
                </b-button>
                <b-button type="is-primary"
                          @click="submitUpload()"
                          icon-pack="fas"
                          icon-left="fas fa-upload"
                          :disabled="uploadButtonDisabled">
                  {{ uploadButtonText }}
                </b-button>
              </footer>

            </div>
          </b-modal>
      % else:
          <div id="upload-worksheet-dialog" style="display: none;">
            <p>
              This will <strong>update</strong> the batch data with the worksheet
              file you provide.&nbsp; Please be certain to use the right one!
            </p>
            ${upload_worksheet_form.render_deform(buttons=False, form_kwargs={'name': 'upload-worksheet'})|n}
          </div>
      % endif
  % endif

  % if not use_buefy:
      % if master.handler.executable(batch) and master.has_perm('execute'):
          <div id="execution-options-dialog" style="display: none;">
            ${execute_form.render_deform(form_kwargs={'name': 'batch-execution'}, buttons=False)|n}
          </div>
      % endif
  % endif

</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  % if use_buefy:
      % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
          ${upload_worksheet_form.render_deform(buttons=False, form_kwargs={'ref': 'actualUploadForm'})|n}
      % endif
      % if master.handler.executable(batch) and master.has_perm('execute'):
          ${execute_form.render_deform(form_kwargs={'ref': 'actualExecuteForm'}, buttons=False)|n}
      % endif
  % endif
</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <${form.component} @show-upload="showUploadDialog = true">
    </${form.component}>
  </div>
</%def>

<%def name="render_row_grid_tools()">
  ${parent.render_row_grid_tools()}
  % if use_buefy and master.rows_bulk_deletable and not batch.executed and master.has_perm('delete_rows'):
      <b-button type="is-danger"
                @click="deleteResultsInit()"
                icon-pack="fas"
                icon-left="trash">
        Delete Results
      </b-button>
      <b-modal has-modal-card
               :active.sync="deleteResultsShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Delete Results</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              This batch has
              <span class="has-text-weight-bold">${batch.rowcount}</span>
              total rows.
            </p>
            <p class="block">
              Your current filters have returned
              <span class="has-text-weight-bold">{{ total }}</span>
              results.
            </p>
            <p class="block">
              Would you like to
              <span class="has-text-danger has-text-weight-bold">
                delete all {{ total }}
              </span>
              results?
            </p>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="deleteResultsShowDialog = false">
              Cancel
            </b-button>
            <once-button type="is-danger"
                         tag="a" href="${url('{}.delete_rows'.format(route_prefix), uuid=batch.uuid)}"
                         icon-left="trash"
                         text="Delete Results">
            </once-button>
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.statusBreakdownData = ${json.dumps(status_breakdown_data)|n}

    ThisPage.methods.autoFilterStatus = function(row) {
        this.$refs.rowGrid.setFilters([
            {key: 'status_code',
             verb: 'equal',
             value: row.code},
        ])
        document.getElementById('rowGrid').scrollIntoView({
            behavior: 'smooth',
        })
    }

    % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):

        ThisPageData.showUploadDialog = false
        ThisPageData.uploadButtonText = "Upload & Update Batch"
        ThisPageData.uploadButtonDisabled = false

        ThisPage.methods.submitUpload = function() {
            let form = this.$refs.uploadForm
            let value = form.field_model_worksheet_file
            if (!value) {
                alert("Please choose a file to upload.")
                return
            }
            this.uploadButtonDisabled = true
            this.uploadButtonText = "Working, please wait..."
            form.submit()
        }

        ${upload_worksheet_form.component_studly}.methods.submit = function() {
            this.$refs.actualUploadForm.submit()
        }

    ## end 'external_worksheet'
    % endif

    % if execute_enabled and master.has_perm('execute'):

        ThisPageData.showExecutionDialog = false

        ThisPage.methods.submitExecuteBatch = function() {
            this.$refs.executeBatchForm.submit()
        }

        ${execute_form.component_studly}.methods.submit = function() {
            this.$refs.actualExecuteForm.submit()
        }

    % endif

    % if master.rows_bulk_deletable and not batch.executed and master.has_perm('delete_rows'):

        ${rows_grid.component_studly}Data.deleteResultsShowDialog = false

        ${rows_grid.component_studly}.methods.deleteResultsInit = function() {
            this.deleteResultsShowDialog = true
        }

    % endif

  </script>
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  % if master.has_worksheet_file and master.allow_worksheet(batch) and master.has_perm('worksheet'):
      <script type="text/javascript">

        ## UploadForm
        ${upload_worksheet_form.component_studly}.data = function() { return ${upload_worksheet_form.component_studly}Data }
        Vue.component('${upload_worksheet_form.component}', ${upload_worksheet_form.component_studly})

      </script>
  % endif

  % if execute_enabled and master.has_perm('execute'):
      <script type="text/javascript">

        ## ExecuteForm
        ${execute_form.component_studly}.data = function() { return ${execute_form.component_studly}Data }
        Vue.component('${execute_form.component}', ${execute_form.component_studly})

      </script>
  % endif
</%def>


${parent.body()}
