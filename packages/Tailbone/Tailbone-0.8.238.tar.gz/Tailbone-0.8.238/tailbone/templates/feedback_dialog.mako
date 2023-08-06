## -*- coding: utf-8; -*-

<%def name="feedback_dialog()">
  <div id="feedback-dialog" style="display: none;">
    ${h.form(url('feedback'))}
    ${h.csrf_token(request)}
    ${h.hidden('user', value=request.user.uuid if request.user else None)}

    <p>
      Questions, suggestions, comments, complaints, etc. <span class="red">regarding this website</span>
      are welcome and may be submitted below.
    </p>

    <div class="field-wrapper referrer">
      <label for="referrer">Referring URL</label>
      <div class="field"></div>
    </div>

    % if request.user:
        ${h.hidden('user_name', value=six.text_type(request.user))}
    % else:
        <div class="field-wrapper">
          <label for="user_name">Your Name</label>
          <div class="field">
            ${h.text('user_name')}
          </div>
        </div>
    % endif

    <div class="field-wrapper">
      <label for="referrer">Message</label>
      <div class="field">
        ${h.textarea('message', cols=45, rows=15)}
      </div>
    </div>

    ${h.end_form()}
  </div>
</%def>
