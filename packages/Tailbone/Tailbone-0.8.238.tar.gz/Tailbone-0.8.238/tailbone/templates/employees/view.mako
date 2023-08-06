## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  ${view_profiles_helper([instance.person])}
</%def>

${parent.body()}
