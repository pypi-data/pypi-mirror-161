## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Workflows</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      Users can only choose from the workflows enabled below.
    </p>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_scratch"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_scratch']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Scratch
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_invoice"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_invoice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Invoice
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_purchase_order"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_purchase_order']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Purchase Order
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_receiving_from_purchase_order_with_invoice"
                  v-model="simpleSettings['rattail.batch.purchase.allow_receiving_from_purchase_order_with_invoice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        From Purchase Order, with Invoice
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_truck_dump_receiving"
                  v-model="simpleSettings['rattail.batch.purchase.allow_truck_dump_receiving']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Truck Dump
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Vendors</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If set, user must choose a &quot;supported&quot; vendor; otherwise they may choose &quot;any&quot; vendor.">
      <b-checkbox name="rattail.batch.purchase.supported_vendors_only"
                  v-model="simpleSettings['rattail.batch.purchase.supported_vendors_only']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Only allow batch for "supported" vendors
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Display</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.show_ordered_column_in_grid"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.show_ordered_column_in_grid']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "ordered" quantities in row grid
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.receiving.show_shipped_column_in_grid"
                  v-model="simpleSettings['rattail.batch.purchase.receiving.show_shipped_column_in_grid']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show "shipped" quantities in row grid
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Product Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="NB. Allow Cases setting also affects Ordering behavior.">
      <b-checkbox name="rattail.batch.purchase.allow_cases"
                  v-model="simpleSettings['rattail.batch.purchase.allow_cases']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow Cases
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.batch.purchase.allow_expired_credits"
                  v-model="simpleSettings['rattail.batch.purchase.allow_expired_credits']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "Expired" Credits
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Mobile Interface</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="TODO: this may also affect Ordering (?)">
      <b-checkbox name="rattail.batch.purchase.mobile_images"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_images']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Show Product Images
      </b-checkbox>
    </b-field>

    <b-field message="If set, one or more &quot;quick receive&quot; buttons will be available for mobile receiving.">
      <b-checkbox name="rattail.batch.purchase.mobile_quick_receive"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_quick_receive']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "Quick Receive"
      </b-checkbox>
    </b-field>

    <b-field message="If set, only a &quot;quick receive all&quot; button will be shown.  Only applicable if quick receive (above) is enabled.">
      <b-checkbox name="rattail.batch.purchase.mobile_quick_receive_all"
                  v-model="simpleSettings['rattail.batch.purchase.mobile_quick_receive_all']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Quick Receive "All or Nothing"
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
