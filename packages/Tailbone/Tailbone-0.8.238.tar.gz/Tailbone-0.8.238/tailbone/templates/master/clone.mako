## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Clone ${model_title}: ${instance_title}</%def>

<%def name="render_buefy_form()">
  <br />
  % if use_buefy:
      <b-notification :closable="false">
        You are about to clone the following ${model_title} as a new record:
      </b-notification>
  % else:
  <p>You are about to clone the following ${model_title} as a new record:</p>
  % endif

  ${parent.render_buefy_form()}
</%def>

<%def name="render_form_buttons()">
  <br />
  % if use_buefy:
      <b-notification :closable="false">
        Are you sure about this?
      </b-notification>
  % else:
  <p>Are you sure about this?</p>
  % endif
  <br />

  % if use_buefy:
  ${h.form(request.current_route_url(), **{'@submit': 'submitForm'})}
  % else:
  ${h.form(request.current_route_url(), class_='autodisable')}
  % endif
  ${h.csrf_token(request)}
  ${h.hidden('clone', value='clone')}
    <div class="buttons">
      % if use_buefy:
          <once-button tag="a" href="${form.cancel_url}"
                       text="Whoops, nevermind...">
          </once-button>
          <b-button type="is-primary"
                    native-type="submit"
                    :disabled="formSubmitting">
            {{ submitButtonText }}
          </b-button>
      % else:
          ${h.link_to("Whoops, nevermind...", form.cancel_url, class_='button autodisable')}
          ${h.submit('submit', "Yes, please clone away")}
      % endif
    </div>
  ${h.end_form()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.formSubmitting = false
    TailboneFormData.submitButtonText = "Yes, please clone away"

    TailboneForm.methods.submitForm = function() {
        this.formSubmitting = true
        this.submitButtonText = "Working, please wait..."
    }

  </script>
</%def>


${parent.body()}
