## -*- coding: utf-8; -*-
<%inherit file="/master/view_row.mako" />

<%def name="render_buefy_form()">
  <div class="form">
    <tailbone-form></tailbone-form>
    <br />
    ${catalog_entry_diff.render_html()}
  </div>
</%def>


${parent.body()}
