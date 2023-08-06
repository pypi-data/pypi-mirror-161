## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />
<%namespace file="/messages/recipients.mako" import="message_recipients_template" />

<%def name="content_title()">${parent.content_title() if not use_buefy else ''}</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if use_buefy:
      ${h.javascript_link(request.static_url('tailbone:static/js/tailbone.buefy.message_recipients.js'))}
  % else:
  ${h.javascript_link(request.static_url('tailbone:static/js/lib/tag-it.min.js'))}
  <script type="text/javascript">

    var recipient_mappings = new Map([
        <% last = len(available_recipients) %>
        % for i, recip in enumerate(available_recipients, 1):
            <% uuid, entry = recip %>
            ['${uuid}', ${json.dumps(entry)|n}]${',' if i < last else ''}
        % endfor
    ]);

    // validate message before sending
    function validate_message_form() {
        var form = $('#deform');

        if (! form.find('input[name="set_recipients"]').val()) {
            alert("You must specify some recipient(s) for the message.");
            $('.set_recipients input').data('ui-tagit').tagInput.focus();
            return false;
        }

        if (! form.find('input[name="subject"]').val()) {
            alert("You must provide a subject for the message.");
            form.find('input[name="subject"]').focus();
            return false;
        }

        return true;
    }

    $(function() {

        var recipients = $('.set_recipients input');

        recipients.tagit({

            autocomplete: {
                delay: 0,
                minLength: 2,
                autoFocus: true,
                removeConfirmation: true,

                source: function(request, response) {
                    var term = request.term.toLowerCase();
                    var data = [];
                    recipient_mappings.forEach(function(name, uuid) {
                        if (!name.toLowerCase && name.name) {
                            name = name.name;
                        }
                        if (name.toLowerCase().indexOf(term) >= 0) {
                            data.push({value: uuid, label: name});
                        }
                    });
                    response(data);
                }
            },

            beforeTagAdded: ${self.before_tag_added()},

            beforeTagRemoved: function(event, ui) {

                // Unfortunately we're responsible for cleaning up the hidden
                // field, since the values there do not match the tag labels.
                var tags = recipients.tagit('assignedTags');
                var uuid = ui.tag.data('uuid');
                tags = tags.filter(function(element) {
                    return element != uuid;
                });
                recipients.data('ui-tagit')._updateSingleTagsField(tags);
            }
        });

        // set focus to recipients field
        recipients.data('ui-tagit').tagInput.focus();
    });

  </script>
  ${self.validate_message_js()}
  % endif
</%def>

<%def name="validate_message_js()">
  <script type="text/javascript">
    $(function() {
        $('#new-message').submit(function() {
            return validate_message_form();
        });
    });
  </script>
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
      <style type="text/css">

        .this-page-content {
          width: 100%;
        }

        .this-page-content .buttons {
            margin-left: 20rem;
        }

      </style>
  % else:
  ${h.stylesheet_link(request.static_url('tailbone:static/css/jquery.tagit.css'))}
  <style type="text/css">

    .recipients input {
        min-width: 525px;
    }

    .subject input {
        min-width: 540px;
    }

    .body textarea {
        min-width: 540px;
    }

  </style>
  % endif
</%def>

<%def name="before_tag_added()">
    function(event, ui) {

        // Lookup the name in cached mapping, and show that on the tag, instead
        // of the UUID.  The tagit widget should take care of keeping the
        // hidden field in sync for us, still using the UUID.
        var uuid = ui.tagLabel;
        var name = recipient_mappings.get(uuid);
        ui.tag.find('.tagit-label').html(name);
    }
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.list'):
      <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
      <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
      <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
  % endif
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  ${message_recipients_template()}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.possibleRecipients = new Map(${json.dumps(available_recipients)|n})
    TailboneFormData.recipientDisplayMap = ${json.dumps(recipient_display_map)|n}

  </script>
</%def>


${parent.body()}
