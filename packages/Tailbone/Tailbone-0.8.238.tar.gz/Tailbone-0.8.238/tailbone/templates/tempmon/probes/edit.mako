## -*- coding: utf-8 -*-
<%inherit file="/master/edit.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <script type="text/javascript">
    $(function() {

        $('.field-wrapper.client_uuid select').selectmenu();

        $('.field-wrapper.appliance_type select').selectmenu();

    });
  </script>
</%def>

${parent.body()}
