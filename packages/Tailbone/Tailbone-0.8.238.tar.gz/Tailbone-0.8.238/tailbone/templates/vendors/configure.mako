## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, vendor chooser is an autocomplete field.">
      <b-checkbox name="rattail.vendors.choice_uses_dropdown"
                  v-model="simpleSettings['rattail.vendors.choice_uses_dropdown']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show vendor chooser as dropdown (select) element
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Supported Vendors</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      The following vendor "keys" are defined within various places in
      the software.&nbsp; You must identify each explicitly with a
      Vendor record, for things to work as designed.
    </p>

    <b-field v-for="setting in supportedVendorSettings"
             :key="setting.key"
             horizontal
             :label="setting.key"
             :type="supportedVendorSettings[setting.key].value ? null : 'is-warning'"
             style="max-width: 75%;">

      <tailbone-autocomplete :name="'rattail.vendor.' + setting.key"
                             service-url="${url('vendors.autocomplete')}"
                             v-model="supportedVendorSettings[setting.key].value"
                             :initial-label="setting.label"
                             @input="settingsNeedSaved = true">
      </tailbone-autocomplete>
    </b-field>

  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.supportedVendorSettings = ${json.dumps(supported_vendor_settings)|n}

  </script>
</%def>


${parent.body()}
