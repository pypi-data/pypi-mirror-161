## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Generating</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, reports are shown as simple list of hyperlinks.">
      <b-checkbox name="tailbone.reporting.choosing_uses_form"
                  v-model="simpleSettings['tailbone.reporting.choosing_uses_form']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show report chooser as form, with dropdown
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
