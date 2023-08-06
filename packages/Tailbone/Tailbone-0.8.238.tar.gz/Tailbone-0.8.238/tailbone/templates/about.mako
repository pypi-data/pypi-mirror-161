## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">About ${base_meta.app_title()}</%def>

<%def name="page_content()">
  <h2>${project_title} ${project_version}</h2>

  % for name, version in packages.items():
      <h3>${name} ${version}</h3>
  % endfor

  <br />
  <p>Please see <a href="https://rattailproject.org/">rattailproject.org</a> for more info.</p>
</%def>


${parent.body()}
