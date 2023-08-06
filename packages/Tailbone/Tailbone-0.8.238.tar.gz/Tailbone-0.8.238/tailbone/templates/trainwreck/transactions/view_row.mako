## -*- coding: utf-8; -*-
<%inherit file="/master/view_row.mako" />

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    % if discounts_data is not Undefined:
        ${form.component_studly}Data.discountsData = ${json.dumps(discounts_data)|n}
    % endif

  </script>
</%def>


${parent.body()}
