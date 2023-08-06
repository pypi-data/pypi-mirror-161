## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <p class="block has-text-weight-bold is-italic">
    NB.&nbsp; Any changes made here will require an app restart!
  </p>

  % for topkey, topgroup in sorted(view_settings.items(), key=lambda itm: 'aaaa' if itm[0] == 'rattail' else itm[0]):
      <h3 class="block is-size-3">Views for:&nbsp; ${topkey}</h3>
      % for group_key, group in six.iteritems(topgroup):
          <h4 class="block is-size-4">${group_key.capitalize()}</h4>
          % for key, label in group:
              ${self.simple_flag(key, label)}
          % endfor
      % endfor
  % endfor

</%def>

<%def name="simple_flag(key, label)">
  <b-field label="${label}" horizontal>
    <b-select name="tailbone.includes.${key}"
              v-model="simpleSettings['tailbone.includes.${key}']"
              @input="settingsNeedSaved = true">
      <option :value="null">(disabled)</option>
      % for option in view_options[key]:
          <option value="${option}">${option}</option>
      % endfor
    </b-select>
  </b-field>
</%def>


${parent.body()}
