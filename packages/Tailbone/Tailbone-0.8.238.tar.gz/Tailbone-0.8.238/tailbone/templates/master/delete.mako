## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Delete ${model_title}: ${instance_title}</%def>

<%def name="context_menu_items()">
  % if not use_buefy and master.viewable and master.has_perm('view'):
      <li>${h.link_to("View this {}".format(model_title), action_url('view', instance))}</li>
  % endif
  % if not use_buefy and master.editable and master.has_perm('edit'):
      <li>${h.link_to("Edit this {}".format(model_title), action_url('edit', instance))}</li>
  % endif
  % if not use_buefy and master.creatable and master.show_create_link and master.has_perm('create'):
      % if master.creates_multiple:
          <li>${h.link_to("Create new {}".format(model_title_plural), url('{}.create'.format(route_prefix)))}</li>
      % else:
          <li>${h.link_to("Create a new {}".format(model_title), url('{}.create'.format(route_prefix)))}</li>
      % endif
  % endif
</%def>

<%def name="render_buefy_form()">
  <br />
  % if use_buefy:
      <b-notification type="is-danger" :closable="false">
        You are about to delete the following ${model_title} and all associated data:
      </b-notification>
  % else:
  <p>You are about to delete the following ${model_title} and all associated data:</p>
  % endif

  ${parent.render_buefy_form()}
</%def>

<%def name="render_form_buttons()">
  <br />
  % if use_buefy:
      <b-notification type="is-danger" :closable="false">
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
    <div class="buttons">
      % if use_buefy:
          <once-button tag="a" href="${form.cancel_url}"
                       text="Whoops, nevermind...">
          </once-button>
          <b-button type="is-primary is-danger"
                    native-type="submit"
                    :disabled="formSubmitting">
            {{ formButtonText }}
          </b-button>
      % else:
      <a class="button" href="${form.cancel_url}">Whoops, nevermind...</a>
      ${h.submit('submit', "Yes, please DELETE this data forever!", class_='button is-primary')}
      % endif
    </div>
  ${h.end_form()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.formSubmitting = false
    TailboneFormData.formButtonText = "Yes, please DELETE this data forever!"

    TailboneForm.methods.submitForm = function() {
        this.formSubmitting = true
        this.formButtonText = "Working, please wait..."
    }

  </script>
</%def>


${parent.body()}
