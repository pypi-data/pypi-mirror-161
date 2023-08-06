## -*- coding: utf-8 -*-
<%inherit file="/master/create.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    // TODO: this variable name should be more dynamic (?) since this is
    // connected to (and only here b/c of) the permissions field
    TailboneFormData.showingPermissionGroup = ''

  </script>
</%def>

${parent.body()}
