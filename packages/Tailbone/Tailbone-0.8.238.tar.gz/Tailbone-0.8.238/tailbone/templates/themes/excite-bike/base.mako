## -*- coding: utf-8; -*-
<%inherit file="tailbone:templates/base.mako" />

<%def name="jquery_theme()">
  ${h.stylesheet_link('https://code.jquery.com/ui/1.11.4/themes/excite-bike/jquery-ui.css')}
</%def>

${parent.body()}
