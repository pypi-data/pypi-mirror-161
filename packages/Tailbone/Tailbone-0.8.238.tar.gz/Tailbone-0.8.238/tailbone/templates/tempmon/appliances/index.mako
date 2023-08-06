## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

  .grid .image-frame {
      height: 150px;
      text-align: center;
      white-space: nowrap;
      width: 150px;
  }

  .grid .image-helper {
      display: inline-block;
      height: 100%;
      vertical-align: middle;
  }

  .grid img {
      vertical-align: middle;
      max-height: 150px;
      max-width: 150px;
  }

  </style>
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('tempmon.appliances.dashboard'):
      <li>${h.link_to("Go to the Dashboard", url('tempmon.dashboard'))}</li>
  % endif
</%def>


${parent.body()}
