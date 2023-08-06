## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="title()">New ${row_model_title}</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to {}".format(model_title), index_url)}</li>
</%def>

${parent.body()}
