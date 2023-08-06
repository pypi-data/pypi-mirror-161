## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Customer Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field message="If not set, only a Person is required.">
      <b-checkbox name="rattail.custorders.new_order_requires_customer"
                  v-model="simpleSettings['rattail.custorders.new_order_requires_customer']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Require a Customer account
      </b-checkbox>
    </b-field>

    <b-field message="If not set, default contact info is always assumed.">
      <b-checkbox name="rattail.custorders.new_orders.allow_contact_info_choice"
                  v-model="simpleSettings['rattail.custorders.new_orders.allow_contact_info_choice']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow user to choose contact info
      </b-checkbox>
    </b-field>

    <b-field message="Only applies if user is allowed to choose contact info.">
      <b-checkbox name="rattail.custorders.new_orders.allow_contact_info_create"
                  v-model="simpleSettings['rattail.custorders.new_orders.allow_contact_info_create']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow user to enter new contact info
      </b-checkbox>
    </b-field>

    <p class="block">
      If you allow users to enter new contact info, the default action
      when the order is submitted, is to send email with details of
      the new contact info.&nbsp; Settings for these are at:
    </p>

    <ul class="list">
      <li class="list-item">
        ${h.link_to("New Phone Request", url('emailprofiles.view', key='new_phone_requested'))}
      </li>
      <li class="list-item">
        ${h.link_to("New Email Request", url('emailprofiles.view', key='new_email_requested'))}
      </li>
    </ul>
  </div>

  <h3 class="block is-size-3">Product Handling</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.custorders.allow_case_orders"
                  v-model="simpleSettings['rattail.custorders.allow_case_orders']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "case" orders
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.allow_unit_orders"
                  v-model="simpleSettings['rattail.custorders.allow_unit_orders']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "unit" orders
      </b-checkbox>
    </b-field>

    <b-field>
      <b-checkbox name="rattail.custorders.product_price_may_be_questionable"
                  v-model="simpleSettings['rattail.custorders.product_price_may_be_questionable']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow prices to be flagged as "questionable"
      </b-checkbox>
    </b-field>

    <b-field message="If set, user can enter details of an arbitrary new &quot;pending&quot; product.">
      <b-checkbox name="rattail.custorders.allow_unknown_product"
                  v-model="simpleSettings['rattail.custorders.allow_unknown_product']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow creating orders for "unknown" products
      </b-checkbox>
    </b-field>

  </div>
</%def>


${parent.body()}
