## -*- coding: utf-8 -*-
<%inherit file="/messages/index.mako" />

<%def name="title()">Sent Messages</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <li>${h.link_to("Go to my Message Inbox", url('messages.inbox'))}</li>
  <li>${h.link_to("Go to my Message Archive", url('messages.archive'))}</li>
</%def>

${parent.body()}
