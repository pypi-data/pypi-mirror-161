## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    $(function() {

        $('.field-wrapper.recipients .more').click(function() {
            $(this).hide();
            $(this).siblings('.everyone').css('display', 'inline-block');
            return false;
        });

        $('.field-wrapper.recipients .everyone').click(function() {
            $(this).hide();
            $(this).siblings('.more').show();
        });

    });

  </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
      <style type="text/css">
        .everyone {
            cursor: pointer;
        }
        .tailbone-message-body {
            margin: 1rem auto;
            min-height: 10rem;
        }
        .tailbone-message-body p {
            margin-bottom: 1rem;
        }
      </style>
  % else:
  <style type="text/css">
    .recipients .everyone {
        cursor: pointer;
        display: none;
    }
    .message-tools {
        margin-bottom: 15px;
    }
    .message-body {
        border-top: 1px solid black;
        border-bottom: 1px solid black;
        margin-bottom: 15px;
        padding: 0 5em;
        white-space: pre-line;
    }
    .message-body p {
        margin-bottom: 15px;
    }
  </style>
  % endif
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.create'):
      <li>${h.link_to("Send a new Message", url('messages.create'))}</li>
  % endif
  % if recipient:
      % if recipient.status == enum.MESSAGE_STATUS_INBOX:
          <li>${h.link_to("Back to Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
      % else:
          <li>${h.link_to("Back to Message Archive", url('messages.archive'))}</li>
          <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
          <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
      % endif
  % else:
      <li>${h.link_to("Back to Sent Messages", url('messages.sent'))}</li>
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
  % endif
</%def>

<%def name="message_tools()">
  % if recipient:
      % if use_buefy:
          <div class="buttons">
            % if request.has_perm('messages.create'):
                <once-button type="is-primary"
                             tag="a" href="${url('messages.reply', uuid=instance.uuid)}"
                             text="Reply">
                </once-button>
                <once-button type="is-primary"
                             tag="a" href="${url('messages.reply_all', uuid=instance.uuid)}"
                             text="Reply to All">
                </once-button>
            % endif
            % if recipient.status == enum.MESSAGE_STATUS_INBOX:
                <once-button type="is-primary"
                             tag="a" href="${url('messages.move', uuid=instance.uuid)}?dest=archive"
                             text="Move to Archive">
                </once-button>
            % else:
                <once-button type="is-primary"
                             tag="a" href="${url('messages.move', uuid=instance.uuid)}?dest=inbox"
                             text="Move to Inbox">
                </once-button>
            % endif
          </div>
      % else:
          <div class="message-tools">
            % if request.has_perm('messages.create'):
                ${h.link_to("Reply", url('messages.reply', uuid=instance.uuid), class_='button')}
                ${h.link_to("Reply to All", url('messages.reply_all', uuid=instance.uuid), class_='button')}
            % endif
            % if recipient.status == enum.MESSAGE_STATUS_INBOX:
                ${h.link_to("Move to Archive", url('messages.move', uuid=instance.uuid) + '?dest=archive', class_='button')}
            % else:
                ${h.link_to("Move to Inbox", url('messages.move', uuid=instance.uuid) + '?dest=inbox', class_='button')}
            % endif
          </div>
      % endif
  % endif
</%def>

<%def name="message_body()">
  ${instance.body}
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  % if use_buefy:
      <br />
      <div style="margin-left: 5rem;">
        ${self.message_tools()}
        <div class="tailbone-message-body">
          ${self.message_body()}
        </div>
        ${self.message_tools()}
      </div>
  % else:
      ${self.message_tools()}
      <div class="message-body">
        ${self.message_body()}
      </div>
      ${self.message_tools()}
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.showingAllRecipients = false

    TailboneForm.methods.showMoreRecipients = function() {
        this.showingAllRecipients = true
    }

    TailboneForm.methods.hideMoreRecipients = function() {
        this.showingAllRecipients = false
    }

  </script>
</%def>


${parent.body()}
