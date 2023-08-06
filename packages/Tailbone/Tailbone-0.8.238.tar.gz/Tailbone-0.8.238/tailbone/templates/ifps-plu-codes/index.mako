## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <li>${h.link_to("Go to IFPS Website", 'https://www.ifpsglobal.com/PLU-Codes/PLU-codes-Search', target='_blank')}</li>
</%def>


${parent.body()}
