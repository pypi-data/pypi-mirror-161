## -*- coding: utf-8; -*-
<%inherit file="/master/edit.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
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
