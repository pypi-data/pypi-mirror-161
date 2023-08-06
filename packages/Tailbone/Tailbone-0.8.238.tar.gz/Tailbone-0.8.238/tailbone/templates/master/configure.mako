## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="page_content()">
  ${parent.page_content()}

  <h3 class="block is-size-3">TODO</h3>

  <p class="block">
    You should create a custom template file at:&nbsp;
    <span class="is-family-monospace">${master.get_template_prefix()}/configure.mako</span>
  </p>

  <p class="block">
    Within that you should define (at least) the
    <span class="is-family-monospace">page_content()</span>
    def block.
  </p>

  <p class="block">
    You can see the following examples for reference:
  </p>

  <ul class="block">
    <li class="is-family-monospace">/datasync/configure.mako</li>
    <li class="is-family-monospace">/importing/configure.mako</li>
    <li class="is-family-monospace">/products/configure.mako</li>
    <li class="is-family-monospace">/receiving/configure.mako</li>
  </ul>

</%def>


${parent.body()}
