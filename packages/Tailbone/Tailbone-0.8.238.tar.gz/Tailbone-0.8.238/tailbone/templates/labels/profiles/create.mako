## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">

    div.form div.field-wrapper.format textarea {
        font-size: 120%;
        font-family: monospace;
        width: auto;
    }

  </style>
</%def>

${parent.body()}
