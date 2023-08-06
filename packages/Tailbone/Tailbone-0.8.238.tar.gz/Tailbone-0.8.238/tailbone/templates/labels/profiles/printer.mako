## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Printer Settings</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Label Profiles", url('labelprofiles'))}</li>
  <li>${h.link_to("View this Label Profile", url('labelprofiles.view', uuid=profile.uuid))}</li>
  <li>${h.link_to("Edit this Label Profile", url('labelprofiles.edit', uuid=profile.uuid))}</li>
</%def>


${parent.body()}
