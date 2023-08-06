## -*- coding: utf-8; -*-

% if not readonly:
<% _focus_rendered = False %>
${h.form(form.action_url, id=dform.formid, method='post', enctype='multipart/form-data', **form_kwargs)}
${h.csrf_token(request)}
% endif

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

% for field in form.fields:

    ## % if readonly or field.name in readonly_fields:
    % if readonly:
        ${render_field_readonly(field)|n}
    % elif field not in dform and field in form.readonly_fields:
        ${render_field_readonly(field)|n}
    % elif field in dform:
        <% field = dform[field] %>

        % if form.field_visible(field.name):
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

            ## % if not _focus_rendered and (fieldset.focus is True or fieldset.focus is field):
            % if not readonly and not _focus_rendered:
                ## % if not field.is_readonly() and getattr(field.renderer, 'needs_focus', True):
                % if not field.widget.readonly:
                    <script type="text/javascript">
                      $(function() {
    ##                       % if hasattr(field.renderer, 'focus_name'):
    ##                           $('#${field.renderer.focus_name}').focus();
    ##                       % else:
    ##                           $('#${field.renderer.name}').focus();
    ##                       % endif
                          $('#${field.oid}').focus();
                      });
                    </script>
                    <% _focus_rendered = True %>
                % endif
            % endif

        % else:
            ## hidden field
            ${field.serialize()|n}
        % endif

    % endif

% endfor

% if buttons:
    ${buttons|n}
% elif not readonly and (buttons is Undefined or (buttons is not None and buttons is not False)):
    <div class="buttons">
      ## ${h.submit('create', form.create_label if form.creating else form.update_label)}
      ${h.submit('save', getattr(form, 'submit_label', getattr(form, 'save_label', "Submit")), class_='button is-primary')}
##         % if form.creating and form.allow_successive_creates:
##             ${h.submit('create_and_continue', form.successive_create_label)}
##         % endif
      % if getattr(form, 'show_reset', False):
          <input type="reset" value="Reset" class="button" />
      % endif
      % if getattr(form, 'show_cancel', True):
          ${h.link_to("Cancel", form.cancel_url, class_='cancel button{}'.format(' autodisable' if form.auto_disable_cancel else ''))}
      % endif
    </div>
% endif

% if not readonly:
${h.end_form()}
% endif
