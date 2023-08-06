## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">POS</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.customers.active_in_pos"
                  v-model="simpleSettings['rattail.customers.active_in_pos']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Expose/track the "Active in POS" flag for customers.
      </b-checkbox>
    </b-field>

  </div>

</%def>


${parent.body()}
