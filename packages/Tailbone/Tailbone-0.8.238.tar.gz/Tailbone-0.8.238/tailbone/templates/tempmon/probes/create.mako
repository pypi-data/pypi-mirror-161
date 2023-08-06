## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  <script type="text/javascript">
    $(function() {

        $('.field-wrapper.client_uuid select').selectmenu();

        $('.field-wrapper.appliance_type select').selectmenu();

    });
  </script>
</%def>

${parent.body()}
