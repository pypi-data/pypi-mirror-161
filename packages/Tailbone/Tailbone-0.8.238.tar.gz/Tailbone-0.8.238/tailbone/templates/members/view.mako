## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  <% people = h.OrderedDict() %>
  % if instance.person:
      <% people[instance.person.uuid] = instance.person %>
  % endif
  % if instance.customer:
      % for person in instance.customer.people:
          <% people[person.uuid] = person %>
      % endfor
  % endif
  ${view_profiles_helper(people.values())}
</%def>

${parent.body()}
