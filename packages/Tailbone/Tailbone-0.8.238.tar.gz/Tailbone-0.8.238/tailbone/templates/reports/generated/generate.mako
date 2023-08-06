## -*- coding: utf-8; -*-
<%inherit file="/master/form.mako" />

<%def name="title()">${index_title} &raquo; ${report.name}</%def>

<%def name="content_title()">New Report:&nbsp; ${report.name}</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <p style="padding: 1em;">${report.__doc__}</p>
    <br />
    <tailbone-form></tailbone-form>
  </div>
</%def>

<%def name="render_form()">
  % if not use_buefy:
  <p style="padding: 1em;">${report.__doc__}</p>
  % endif
  ${parent.render_form()}
</%def>

${parent.body()}
