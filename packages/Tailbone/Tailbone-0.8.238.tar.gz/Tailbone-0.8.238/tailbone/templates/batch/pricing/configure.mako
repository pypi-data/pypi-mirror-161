## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Options</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.batch.pricing.allow_future"
                  v-model="simpleSettings['rattail.batch.pricing.allow_future']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "future" pricing
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
