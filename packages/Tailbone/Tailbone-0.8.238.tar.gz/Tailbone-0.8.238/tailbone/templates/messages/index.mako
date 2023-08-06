## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    var destination = null;

    function update_move_button() {
        var count = $('.grid tr:not(.header) td.checkbox input:checked').length;
        $('form[name="move-selected"] button')
            .button('option', 'label', "Move " + count + " selected to " + destination)
            .button('option', 'disabled', count < 1);
    }

    $(function() {

        update_move_button();

        $('.grid-wrapper').on('change', 'tr.header td.checkbox input', function() {
            update_move_button();
        });

        $('.grid-wrapper').on('click', 'tr:not(.header) td.checkbox input', function() {
            update_move_button();
        });

        $('form[name="move-selected"]').submit(function() {
            var uuids = [];
            $('.grid tr:not(.header) td.checkbox input:checked').each(function() {
                uuids.push($(this).parents('tr:first').data('uuid'));
            });
            if (! uuids.length) {
                return false;
            }
            $(this).find('[name="uuids"]').val(uuids.toString());
            $(this).find('button')
                .button('option', 'label', "Moving " + uuids.length + " messages to " + destination + "...")
                .button('disable');
        });

    });

  </script>
  % endif
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('messages.create'):
      <li>${h.link_to("Send a new Message", url('messages.create'))}</li>
  % endif
</%def>

<%def name="grid_tools()">
  % if request.matched_route.name in ('messages.inbox', 'messages.archive'):
      % if use_buefy:
          ${h.form(url('messages.move_bulk'), **{'@submit': 'moveMessagesSubmit'})}
          ${h.csrf_token(request)}
          ${h.hidden('destination', value='archive' if request.matched_route.name == 'messages.inbox' else 'inbox')}
          ${h.hidden('uuids', v_model='selected_uuids')}
          <b-button type="is-primary"
                    native-type="submit"
                    :disabled="moveMessagesSubmitting || !checkedRows.length">
            {{ moveMessagesTextCurrent }}
          </b-button>
          ${h.end_form()}
      % else:
          ${h.form(url('messages.move_bulk'), name='move-selected')}
          ${h.csrf_token(request)}
          ${h.hidden('destination', value='archive' if request.matched_route.name == 'messages.inbox' else 'inbox')}
          ${h.hidden('uuids')}
          <button type="submit">Move 0 selected to ${'Archive' if request.matched_route.name == 'messages.inbox' else 'Inbox'}</button>
          ${h.end_form()}
      % endif
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if request.matched_route.name in ('messages.inbox', 'messages.archive'):
      <script type="text/javascript">

        TailboneGridData.moveMessagesSubmitting = false
        TailboneGridData.moveMessagesText = null

        TailboneGrid.computed.moveMessagesTextCurrent = function() {
            if (this.moveMessagesText) {
                return this.moveMessagesText
            }
            let count = this.checkedRows.length
            return "Move " + count.toString() + " selected to ${'Archive' if request.matched_route.name == 'messages.inbox' else 'Inbox'}"
        }

        TailboneGrid.methods.moveMessagesSubmit = function() {
            this.moveMessagesSubmitting = true
            this.moveMessagesText = "Working, please wait..."
        }

      </script>
  % endif
</%def>


${parent.body()}
