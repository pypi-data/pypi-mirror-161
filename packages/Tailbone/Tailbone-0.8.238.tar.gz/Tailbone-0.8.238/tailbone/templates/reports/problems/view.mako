## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if master.has_perm('execute'):
      <nav class="panel">
        <p class="panel-heading">Tools</p>
        <div class="panel-block buttons">
          <b-button type="is-primary"
                    @click="runReportShowDialog = true"
                    icon-pack="fas"
                    icon-left="arrow-circle-right">
            Run this Report
          </b-button>
        </div>
      </nav>

      <b-modal has-modal-card
               :active.sync="runReportShowDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">Run Problem Report</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              You can run this problem report right now if you like.
            </p>

            <p class="block">
              Keep in mind the following may receive email, should the
              report find any problems.
            </p>

            <ul>
              % for recip in instance['email_recipients']:
                  <li>${recip}</li>
              % endfor
            </ul>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="runReportShowDialog = false">
              Cancel
            </b-button>
            ${h.form(master.get_action_url('execute', instance))}
            ${h.csrf_token(request)}
            <b-button type="is-primary"
                      native-type="submit"
                      @click="runReportSubmitting = true"
                      :disabled="runReportSubmitting"
                      icon-pack="fas"
                      icon-left="arrow-circle-right">
              {{ runReportSubmitting ? "Working, please wait..." : "Run Problem Report" }}
            </b-button>
            ${h.end_form()}
          </footer>
        </div>
      </b-modal>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.runReportShowDialog = false
    ThisPageData.runReportSubmitting = false

  </script>
</%def>


${parent.body()}
