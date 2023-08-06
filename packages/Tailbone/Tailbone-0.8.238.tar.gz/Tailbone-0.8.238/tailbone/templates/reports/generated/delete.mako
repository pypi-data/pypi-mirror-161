## -*- coding: utf-8; -*-
<%inherit file="/master/delete.mako" />

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    % if params_data is not Undefined:
        ${form.component_studly}Data.paramsData = ${json.dumps(params_data)|n}
    % endif

  </script>
</%def>


${parent.body()}
