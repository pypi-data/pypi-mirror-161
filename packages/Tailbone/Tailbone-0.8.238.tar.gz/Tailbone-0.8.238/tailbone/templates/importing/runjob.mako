## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    .tailbone-markdown p {
        margin-bottom: 1.5rem;
        margin-top: 1rem;
    }

  </style>
</%def>

<%def name="title()">
  Run ${handler.direction.capitalize()}:&nbsp; ${handler.get_generic_title()}
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('view'):
      <li>${h.link_to("View this {}".format(model_title), action_url('view', handler_info))}</li>
  % endif
</%def>

<%def name="render_this_page()">
  % if 'rattail.importing.runjob.notes' in request.session:
      <b-notification type="is-info tailbone-markdown">
        ${request.session['rattail.importing.runjob.notes']|n}
      </b-notification>
      <% del request.session['rattail.importing.runjob.notes'] %>
  % endif

  ${parent.render_this_page()}
</%def>

<%def name="render_form_buttons()">
  <br />
  ${h.hidden('runjob', **{':value': 'runJob'})}
  <div class="buttons">
    <once-button tag="a" href="${form.cancel_url or request.get_referrer()}"
                 text="Cancel">
    </once-button>
    <b-button type="is-primary"
              @click="submitRun()"
              % if handler.safe_for_web_app:
              :disabled="submittingRun"
              % else:
              disabled
              title="Handler is not (yet) safe to run with this tool"
              % endif
              icon-pack="fas"
              icon-left="arrow-circle-right">
      {{ submittingRun ? "Working, please wait..." : "Run this ${handler.direction.capitalize()}" }}
    </b-button>
    <b-button @click="submitExplain()"
              :disabled="submittingExplain"
              icon-pack="fas"
              icon-left="question-circle">
      {{ submittingExplain ? "Working, please wait..." : "Just show me the notes" }}
    </b-button>
  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ${form.component_studly}Data.submittingRun = false
    ${form.component_studly}Data.submittingExplain = false
    ${form.component_studly}Data.runJob = false

    ${form.component_studly}.methods.submitRun = function() {
        this.submittingRun = true
        this.runJob = true
        this.$nextTick(() => {
            this.$refs.${form.component_studly}.submit()
        })
    }

    ${form.component_studly}.methods.submitExplain = function() {
        this.submittingExplain = true
        this.$refs.${form.component_studly}.submit()
    }

  </script>
</%def>

${parent.body()}
