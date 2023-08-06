## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field grouped>

      <b-field label="Key Field">
        <b-select name="rattail.product.key"
                  v-model="simpleSettings['rattail.product.key']"
                  @input="updateKeyTitle()">
          <option value="upc">upc</option>
          <option value="item_id">item_id</option>
          <option value="scancode">scancode</option>
        </b-select>
      </b-field>

      <b-field label="Key Field Label">
        <b-input name="rattail.product.key_title"
                 v-model="simpleSettings['rattail.product.key_title']"
                 @input="settingsNeedSaved = true">
        </b-input>
      </b-field>

    </b-field>

    <b-field message="If a product has an image in the DB, that will still be preferred.">
      <b-checkbox name="tailbone.products.show_pod_image"
                  v-model="simpleSettings['tailbone.products.show_pod_image']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "POD" Images as fallback
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If set, GPC values like 002XXXXXYYYYY-Z will be converted to 002XXXXX00000-Z for lokkup">
      <b-checkbox name="rattail.products.convert_type2_for_gpc_lookup"
                  v-model="simpleSettings['rattail.products.convert_type2_for_gpc_lookup']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Auto-convert Type 2 UPC for sake of lookup
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Labels</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="User must also have permission to use this feature.">
      <b-checkbox name="tailbone.products.print_labels"
                  v-model="simpleSettings['tailbone.products.print_labels']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow quick/direct label printing from Products page
      </b-checkbox>
    </b-field>

    <b-field label="Speed Bump Threshold"
             message="Show speed bump when at least this many labels are quick-printed at once.  Empty means never show speed bump.">
      <b-input name="tailbone.products.quick_labels.speedbump_threshold"
               v-model="simpleSettings['tailbone.products.quick_labels.speedbump_threshold']"
               type="number"
               @input="settingsNeedSaved = true"
               style="width: 10rem;">
      </b-input>
    </b-field>

  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPage.methods.getTitleForKey = function(key) {
        switch (key) {
        case 'item_id':
            return "Item ID"
        case 'scancode':
            return "Scancode"
        default:
            return "UPC"
        }
    }

    ThisPage.methods.updateKeyTitle = function() {
        this.simpleSettings['rattail.product.key_title'] = this.getTitleForKey(
            this.simpleSettings['rattail.product.key'])
        this.settingsNeedSaved = true
    }

  </script>
</%def>


${parent.body()}
