## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/perms.css'))}
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if instance.person:
      ${view_profiles_helper([instance.person])}
  % endif
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('preferences'):
      <li>${h.link_to("Edit User Preferences", action_url('preferences', instance))}</li>
  % endif
</%def>


${parent.body()}
