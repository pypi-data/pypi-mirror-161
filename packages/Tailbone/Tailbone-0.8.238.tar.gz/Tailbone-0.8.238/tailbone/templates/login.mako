## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />
<%namespace name="base_meta" file="/base_meta.mako" />

<%def name="title()">Login</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  ${h.javascript_link(request.static_url('tailbone:static/js/login.js'))}
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
      <style type="text/css">
        .logo img {
            display: block;
            margin: 3rem auto;
            max-height: 350px;
            max-width: 800px;
        }

        /* must force a particular label with, in order to make sure */
        /* the username and password inputs are the same size */
        .field.is-horizontal .field-label .label {
            text-align: left;
            width: 6rem;
        }

        .buttons {
            justify-content: right;
        }
      </style>
  % else:
      ${h.stylesheet_link(request.static_url('tailbone:static/css/login.css'))}
  % endif
</%def>

<%def name="logo()">
  ${h.image(image_url, "{} logo".format(capture(base_meta.app_title)))}
</%def>

<%def name="login_form()">
  <div class="form">
    ${form.render_deform(form_kwargs={'data-ajax': 'false'})|n}
  </div>
</%def>

<%def name="render_this_page()">
  ${self.page_content()}
</%def>

<%def name="page_content()">
  <div class="logo">
    ${self.logo()}
  </div>

  % if use_buefy:

      <div class="columns is-centered">
        <div class="column is-narrow">
          <div class="card">
            <div class="card-content">
              <tailbone-form></tailbone-form>
            </div>
          </div>
        </div>
      </div>

  % else:
      ${self.login_form()}
  % endif
</%def>


${parent.body()}
