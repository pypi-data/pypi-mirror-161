## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">User Feedback</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">
    .form p {
        margin: 1em 0;
    }
    div.field-wrapper div.field input[type=text] {
        width: 25em;
    }
    div.field-wrapper div.field textarea {
        width: 50em;
    }
    div.buttons {
        margin-left: 15em;
    }
  </style>
</%def>

<div class="form">
  ${form.begin()}
  ${form.csrf_token()}
  ${form.hidden('user', value=request.user.uuid if request.user else None)}

  <p>
    Questions, suggestions, comments, complaints, etc. regarding this website
    are welcome and may be submitted below.
  </p>
  <p>
    Messages will be delivered to the local IT department, and possibly others.
  </p>

##   % if error:
##       <div class="error">${error}</div>
##   % endif

  % if request.user:
      ${form.field_div('user_name', form.hidden('user_name', value=six.text_type(request.user)) + six.text_type(request.user), label="Your Name")}
  % else:
      ${form.field_div('user_name', form.text('user_name'), label="Your Name")}
  % endif

  ${form.field_div('referrer', form.hidden('referrer', value=request.get_referrer()) + request.get_referrer(), label="Referring URL")}

  ${form.field_div('message', form.textarea('message', rows=15))}

  <div class="buttons">
    ${form.submit('send', "Send Message")}
    ${h.link_to("Cancel", request.get_referrer(), class_='button')}
  </div>

  ${form.end()}
</div>
