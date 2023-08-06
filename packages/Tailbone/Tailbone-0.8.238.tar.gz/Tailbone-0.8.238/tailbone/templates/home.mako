## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">Home</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .logo {
        text-align: center;
    }
    .logo img {
        margin: 3em auto;
        max-height: 350px;
        max-width: 800px;
    }
  </style>
</%def>

<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="page_content()">
  <div class="logo">
    ${h.image(image_url, "{} logo".format(capture(base_meta.app_title)))}
    <h1>Welcome to ${base_meta.app_title()}</h1>
  </div>
</%def>


${parent.body()}
