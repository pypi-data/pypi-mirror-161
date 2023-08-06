## -*- coding: utf-8; -*-
<%inherit file="/messages/index.mako" />

<%def name="title()">Message Inbox</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">
    destination = "Archive";
  </script>
  % endif
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
  <li>${h.link_to("Go to my Sent Messages", url('messages.sent'))}</li>
</%def>


${parent.body()}
