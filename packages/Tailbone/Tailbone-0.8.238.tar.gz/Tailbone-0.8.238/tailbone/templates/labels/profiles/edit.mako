## -*- coding: utf-8 -*-
<%inherit file="/master/edit.mako" />

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

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <% printer = instance.get_printer(request.rattail_config) %>
  % if printer and printer.required_settings:
      <li>${h.link_to("Edit Printer Settings", url('labelprofiles.printer_settings', uuid=instance.uuid))}</li>
  % endif
</%def>

${parent.body()}
