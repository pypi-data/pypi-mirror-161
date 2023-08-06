## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

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
  % if request.has_perm('labelprofiles.edit'):
      <% printer = instance.get_printer(request.rattail_config) %>
      % if printer and printer.required_settings:
          <li>${h.link_to("Edit Printer Settings", url('labelprofiles.printer_settings', uuid=instance.uuid))}</li>
      % endif
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}

  <% printer = instance.get_printer(request.rattail_config) %>
  % if printer and printer.required_settings:
      <h2>Printer Settings</h2>

      <div class="form">
        % for name, display in printer.required_settings.items():
            <div class="field-wrapper">
              <label>${display}</label>
              <div class="field">${instance.get_printer_setting(name) or ''}</div>
            </div>
        % endfor
      </div>

  % endif
</%def>


${parent.body()}
