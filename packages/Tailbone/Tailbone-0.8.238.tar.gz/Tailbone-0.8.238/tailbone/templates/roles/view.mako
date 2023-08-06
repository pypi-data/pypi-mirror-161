## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  % if not use_buefy:
  <h2>Users</h2>

  % if instance is guest_role:
      <p>The guest role is implied for all anonymous users, i.e. when not logged in.</p>
  % elif instance is authenticated_role:
      <p>The authenticated role is implied for all users, but only when logged in.</p>
  % elif users:
      <p>The following users are assigned to this role:</p>
      ${users.render_grid()|n}
  % else:
      <p>There are no users assigned to this role.</p>
  % endif
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    % if users_data is not Undefined:
        ${form.component_studly}Data.usersData = ${json.dumps(users_data)|n}
    % endif

    ThisPage.methods.detachPerson = function(url) {
        ## TODO: this should require POST, but we will add that once
        ## we can assume a Buefy theme is present, to avoid having to
        ## implement the logic in old jquery...
        if (confirm("Are you sure you want to detach this person from this customer account?")) {
            location.href = url
        }
    }

  </script>
</%def>

${parent.body()}
