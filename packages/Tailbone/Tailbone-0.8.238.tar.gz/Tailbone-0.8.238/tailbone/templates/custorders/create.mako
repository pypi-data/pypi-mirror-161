## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />
<%namespace name="product_lookup" file="/products/lookup.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
      <style type="text/css">
        .this-page-content {
            flex-grow: 1;
        }
      </style>
  % endif
</%def>

<%def name="page_content()">
  <br />
  % if use_buefy:
      <customer-order-creator></customer-order-creator>
  % else:
      <p>Sorry, but this page is not supported by your current theme configuration.</p>
  % endif
</%def>

<%def name="order_form_buttons()">
  <div class="level">
    <div class="level-left">
    </div>
    <div class="level-right">
      <div class="level-item">
        <div class="buttons">
          <b-button type="is-primary"
                    @click="submitOrder()"
                    :disabled="submittingOrder"
                    icon-pack="fas"
                    icon-left="fas fa-upload">
            {{ submitOrderButtonText }}
          </b-button>
          <b-button @click="startOverEntirely()"
                    icon-pack="fas"
                    icon-left="fas fa-redo">
            Start Over Entirely
          </b-button>
          <b-button @click="cancelOrder()"
                    type="is-danger"
                    icon-pack="fas"
                    icon-left="fas fa-trash">
            Cancel this Order
          </b-button>
        </div>
      </div>
    </div>
  </div>
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  ${product_lookup.tailbone_product_lookup_template()}

  <script type="text/x-template" id="customer-order-creator-template">
    <div>

      ${self.order_form_buttons()}

      <b-collapse class="panel" :class="customerPanelType"
                  :open.sync="customerPanelOpen">

        <div slot="trigger"
             slot-scope="props"
             class="panel-heading"
             role="button">
          <b-icon pack="fas"
            ## TODO: this icon toggling should work, according to
            ## Buefy docs, but i could not ever get it to work.
            ## what am i missing?
            ## https://buefy.org/documentation/collapse/
            ## :icon="props.open ? 'caret-down' : 'caret-right'">
            ## (for now we just always show caret-right instead)
            icon="caret-right">
          </b-icon>
          <strong v-html="customerPanelHeader"></strong>
        </div>

        <div class="panel-block">
          <div style="width: 100%;">

            <div style="display: flex; flex-direction: row;">
              <div style="flex-grow: 1; margin-right: 1rem;">
                <b-notification :type="customerStatusType"
                                position="is-bottom-right"
                                :closable="false">
                  {{ customerStatusText }}
                </b-notification>
              </div>
              <!-- <div class="buttons"> -->
              <!--   <b-button @click="startOverCustomer()" -->
              <!--             icon-pack="fas" -->
              <!--             icon-left="fas fa-redo"> -->
              <!--     Start Over -->
              <!--   </b-button> -->
              <!-- </div> -->
            </div>

            <br />
            <div class="field">
              <b-radio v-model="contactIsKnown"
                       :native-value="true">
                Customer is already in the system.
              </b-radio>
            </div>

            <div v-show="contactIsKnown"
                 style="padding-left: 10rem; display: flex;">

              <div :style="{'flex-grow': contactNotes.length ? 0 : 1}">

                <b-field label="Customer" grouped>
                  <b-field style="margin-left: 1rem;"
                           :expanded="!contactUUID">
                    <tailbone-autocomplete ref="contactAutocomplete"
                                           v-model="contactUUID"
                                           placeholder="Enter name or phone number"
                                           :initial-label="contactDisplay"
                                           % if new_order_requires_customer:
                                           serviceUrl="${url('{}.customer_autocomplete'.format(route_prefix))}"
                                           % else:
                                           serviceUrl="${url('{}.person_autocomplete'.format(route_prefix))}"
                                           % endif
                                           @input="contactChanged">
                    </tailbone-autocomplete>
                  </b-field>
                  <div v-if="contactUUID">
                    <b-button v-if="contactProfileURL"
                              type="is-primary"
                              tag="a" target="_blank"
                              :href="contactProfileURL"
                              icon-pack="fas"
                              icon-left="external-link-alt">
                      View Profile
                    </b-button>
                    &nbsp;
                    <b-button @click="refreshContact"
                              icon-pack="fas"
                              icon-left="redo"
                              :disabled="refreshingContact">
                      {{ refreshingContact ? "Refreshig" : "Refresh" }}
                    </b-button>
                  </div>
                </b-field>

                <b-field grouped v-show="contactUUID"
                         style="margin-top: 2rem;">

                  <b-field label="Phone Number"
                           style="margin-right: 3rem;">
                    <div class="level">
                      <div class="level-left">
                        <div class="level-item">
                          <div v-if="orderPhoneNumber">
                            <p :class="addOtherPhoneNumber ? 'has-text-success': null">
                              {{ orderPhoneNumber }}
                            </p>
                            <p v-if="addOtherPhoneNumber"
                               class="is-size-7 is-italic has-text-success">
                              will be added to customer record
                            </p>
                          </div>
                          <p v-if="!orderPhoneNumber"
                                class="has-text-danger">
                            (no valid phone number on file)
                          </p>
                        </div>
                        % if allow_contact_info_choice:
                            <div class="level-item"
                                 % if not allow_contact_info_create:
                                 v-if="contactPhones.length &gt; 1"
                                 % endif
                                 >
                              <b-button type="is-primary"
                                        @click="editPhoneNumberInit()"
                                        icon-pack="fas"
                                        icon-left="edit">
                                Edit
                              </b-button>

                              <b-modal has-modal-card
                                       :active.sync="editPhoneNumberShowDialog">
                                <div class="modal-card">

                                  <header class="modal-card-head">
                                    <p class="modal-card-title">Edit Phone Number</p>
                                  </header>

                                  <section class="modal-card-body">

                                    <b-field v-for="phone in contactPhones"
                                             :key="phone.uuid">
                                      <b-radio v-model="existingPhoneUUID"
                                               :native-value="phone.uuid">
                                        {{ phone.type }} {{ phone.number }}
                                        <span v-if="phone.preferred"
                                              class="is-italic">
                                          (preferred)
                                        </span>
                                      </b-radio>
                                    </b-field>

                                    % if allow_contact_info_create:
                                        <b-field>
                                          <b-radio v-model="existingPhoneUUID"
                                                   :native-value="null">
                                            other
                                          </b-radio>
                                        </b-field>

                                        <b-field v-if="!existingPhoneUUID"
                                                 grouped>
                                          <b-input v-model="editPhoneNumberOther">
                                          </b-input>
                                          <b-checkbox v-model="editPhoneNumberAddOther">
                                            add this phone number to customer record
                                          </b-checkbox>
                                        </b-field>
                                    % endif

                                  </section>

                                  <footer class="modal-card-foot">
                                    <b-button type="is-primary"
                                              icon-pack="fas"
                                              icon-left="save"
                                              :disabled="editPhoneNumberSaveDisabled"
                                              @click="editPhoneNumberSave()">
                                      {{ editPhoneNumberSaveText }}
                                    </b-button>
                                    <b-button @click="editPhoneNumberShowDialog = false">
                                      Cancel
                                    </b-button>
                                  </footer>
                                </div>
                              </b-modal>

                            </div>
                        % endif
                      </div>
                    </div>
                  </b-field>

                  <b-field label="Email Address">
                    <div class="level">
                      <div class="level-left">
                        <div class="level-item">
                          <div v-if="orderEmailAddress">
                            <p :class="addOtherEmailAddress ? 'has-text-success' : null">
                              {{ orderEmailAddress }}
                            </p>
                            <p v-if="addOtherEmailAddress"
                               class="is-size-7 is-italic has-text-success">
                              will be added to customer record
                            </p>
                          </div>
                          <span v-if="!orderEmailAddress"
                                class="has-text-danger">
                            (no valid email address on file)
                          </span>
                        </div>
                        % if allow_contact_info_choice:
                            <div class="level-item"
                                 % if not allow_contact_info_create:
                                 v-if="contactEmails.length &gt; 1"
                                 % endif
                                 >
                              <b-button type="is-primary"
                                        @click="editEmailAddressInit()"
                                        icon-pack="fas"
                                        icon-left="edit">
                                Edit
                              </b-button>
                              <b-modal has-modal-card
                                       :active.sync="editEmailAddressShowDialog">
                                <div class="modal-card">

                                  <header class="modal-card-head">
                                    <p class="modal-card-title">Edit Email Address</p>
                                  </header>

                                  <section class="modal-card-body">

                                    <b-field v-for="email in contactEmails"
                                             :key="email.uuid">
                                      <b-radio v-model="existingEmailUUID"
                                               :native-value="email.uuid">
                                        {{ email.type }} {{ email.address }}
                                        <span v-if="email.preferred"
                                              class="is-italic">
                                          (preferred)
                                        </span>
                                      </b-radio>
                                    </b-field>

                                    % if allow_contact_info_create:
                                        <b-field>
                                          <b-radio v-model="existingEmailUUID"
                                                   :native-value="null">
                                            other
                                          </b-radio>
                                        </b-field>

                                        <b-field v-if="!existingEmailUUID"
                                                 grouped>
                                          <b-input v-model="editEmailAddressOther">
                                          </b-input>
                                          <b-checkbox v-model="editEmailAddressAddOther">
                                            add this email address to customer record
                                          </b-checkbox>
                                        </b-field>
                                    % endif

                                  </section>

                                  <footer class="modal-card-foot">
                                    <b-button type="is-primary"
                                              icon-pack="fas"
                                              icon-left="save"
                                              :disabled="editEmailAddressSaveDisabled"
                                              @click="editEmailAddressSave()">
                                      {{ editEmailAddressSaveText }}
                                    </b-button>
                                    <b-button @click="editEmailAddressShowDialog = false">
                                      Cancel
                                    </b-button>
                                  </footer>
                                </div>
                              </b-modal>
                            </div>
                        % endif
                      </div>
                    </div>
                  </b-field>

                </b-field>
              </div>

              <div v-show="contactNotes.length"
                   style="margin-left: 1rem;">
                <b-notification v-for="note in contactNotes"
                                :key="note"
                                type="is-warning"
                                :closable="false">
                  {{ note }}
                </b-notification>
              </div>
            </div>

            <br />
            <div class="field">
              <b-radio v-model="contactIsKnown"
                       :native-value="false">
                Customer is not yet in the system.
              </b-radio>
            </div>

            <div v-if="!contactIsKnown"
                 style="padding-left: 10rem; display: flex;">
              <div>
                <b-field grouped>
                  <b-field label="First Name">
                    <span class="has-text-success">
                      {{ newCustomerFirstName }}
                    </span>
                  </b-field>
                  <b-field label="Last Name">
                    <span class="has-text-success">
                      {{ newCustomerLastName }}
                    </span>
                  </b-field>
                </b-field>
                <b-field grouped>
                  <b-field label="Phone Number">
                    <span class="has-text-success">
                      {{ newCustomerPhone }}
                    </span>
                  </b-field>
                  <b-field label="Email Address">
                    <span class="has-text-success">
                      {{ newCustomerEmail }}
                    </span>
                  </b-field>
                </b-field>
              </div>

              <div>
                <b-button type="is-primary"
                          @click="editNewCustomerInit()"
                          icon-pack="fas"
                          icon-left="edit">
                  Edit New Customer
                </b-button>
              </div>

              <div style="margin-left: 1rem;">
                <b-notification type="is-warning"
                                :closable="false">
                  <p>Duplicate records can be difficult to clean up!</p>
                  <p>Please be sure the customer is not already in the system.</p>
                </b-notification>
              </div>

              <b-modal has-modal-card
                       :active.sync="editNewCustomerShowDialog">
                <div class="modal-card">

                  <header class="modal-card-head">
                    <p class="modal-card-title">Edit New Customer</p>
                  </header>

                  <section class="modal-card-body">
                    <b-field grouped>
                      <b-field label="First Name">
                        <b-input v-model.trim="editNewCustomerFirstName"
                                 ref="editNewCustomerInput">
                        </b-input>
                      </b-field>
                      <b-field label="Last Name">
                        <b-input v-model.trim="editNewCustomerLastName">
                        </b-input>
                      </b-field>
                    </b-field>
                    <b-field grouped>
                      <b-field label="Phone Number">
                        <b-input v-model.trim="editNewCustomerPhone"></b-input>
                      </b-field>
                      <b-field label="Email Address">
                        <b-input v-model.trim="editNewCustomerEmail"></b-input>
                      </b-field>
                    </b-field>
                  </section>

                  <footer class="modal-card-foot">
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="save"
                              :disabled="editNewCustomerSaveDisabled"
                              @click="editNewCustomerSave()">
                      {{ editNewCustomerSaveText }}
                    </b-button>
                    <b-button @click="editNewCustomerShowDialog = false">
                      Cancel
                    </b-button>
                  </footer>
                </div>
              </b-modal>

            </div>

          </div>
        </div> <!-- panel-block -->
      </b-collapse>

      <b-collapse class="panel"
                  open>

        <div slot="trigger"
             slot-scope="props"
             class="panel-heading"
             role="button">
          <b-icon pack="fas"
            ## TODO: this icon toggling should work, according to
            ## Buefy docs, but i could not ever get it to work.
            ## what am i missing?
            ## https://buefy.org/documentation/collapse/
            ## :icon="props.open ? 'caret-down' : 'caret-right'">
            ## (for now we just always show caret-right instead)
            icon="caret-right">
          </b-icon>
          <strong v-html="itemsPanelHeader"></strong>
        </div>

        <div class="panel-block">
          <div>
            <div class="buttons">
              <b-button type="is-primary"
                        icon-pack="fas"
                        icon-left="fas fa-plus"
                        @click="showAddItemDialog()">
                Add Item
              </b-button>
              <b-button v-if="contactUUID"
                        icon-pack="fas"
                        icon-left="fas fa-plus"
                        @click="showAddPastItem()">
                Add Past Item
              </b-button>
            </div>

            <b-modal :active.sync="showingItemDialog">
              <div class="card">
                <div class="card-content">

                  <b-tabs type="is-boxed is-toggle"
                          v-model="itemDialogTabIndex"
                          :animated="false">

                    <b-tab-item label="Product">

                      <div class="field">
                        <b-radio v-model="productIsKnown"
                                 :native-value="true">
                          Product is already in the system.
                        </b-radio>
                      </div>

                      <div v-show="productIsKnown"
                           style="padding-left: 5rem;">

                        <b-field grouped>
                          <p class="label control">
                            Product
                          </p>
                          <b-field :expanded="!productUUID">
                            <tailbone-autocomplete ref="productAutocomplete"
                                                   v-model="productUUID"
                                                   placeholder="Enter UPC or brand, description etc."
                                                   :assigned-label="productDisplay"
                                                   serviceUrl="${url('{}.product_autocomplete'.format(route_prefix))}"
                                                   @input="productChanged">
                            </tailbone-autocomplete>
                          </b-field>

                          <b-button type="is-primary"
                                    v-if="!productUUID"
                                    @click="productFullLookup()"
                                    icon-pack="fas"
                                    icon-left="search">
                            Full Lookup
                          </b-button>

                          <b-button v-if="productUUID"
                                    type="is-primary"
                                    tag="a" target="_blank"
                                    :href="productURL"
                                    :disabled="!productURL"
                                    icon-pack="fas"
                                    icon-left="external-link-alt">
                            View Product
                          </b-button>
                        </b-field>

                        <div v-if="productUUID">

                          <div class="is-pulled-right has-text-centered">
                            <img :src="productImageURL"
                                 style="height: 150px; width: 150px; "/>
                            ## <p>{{ productKey }}</p>
                          </div>

                          <b-field grouped>
                            <b-field :label="productKeyLabel">
                              <span>{{ productKey }}</span>
                            </b-field>

                            <b-field label="Unit Size">
                              <span>{{ productSize }}</span>
                            </b-field>

                            <b-field label="Case Size">
                              <span>{{ productCaseQuantity }}</span>
                            </b-field>

                            <b-field label="Reg. Price"
                                     v-if="productSalePriceDisplay">
                              <span>{{ productUnitRegularPriceDisplay }}</span>
                            </b-field>

                            <b-field label="Unit Price"
                                     v-if="!productSalePriceDisplay">
                              <span
                                % if product_price_may_be_questionable:
                                :class="productPriceNeedsConfirmation ? 'has-background-warning' : ''"
                                % endif
                                >
                                {{ productUnitPriceDisplay }}
                              </span>
                            </b-field>
                            <!-- <b-field label="Last Changed"> -->
                            <!--   <span>2021-01-01</span> -->
                            <!-- </b-field> -->

                            <b-field label="Sale Price"
                                     v-if="productSalePriceDisplay">
                              <span class="has-background-warning">
                                {{ productSalePriceDisplay }}
                              </span>
                            </b-field>

                            <b-field label="Sale Ends"
                                     v-if="productSaleEndsDisplay">
                              <span class="has-background-warning">
                                {{ productSaleEndsDisplay }}
                              </span>
                            </b-field>

                          </b-field>

                          % if product_price_may_be_questionable:
                          <b-checkbox v-model="productPriceNeedsConfirmation"
                                      type="is-warning"
                                      size="is-small">
                            This price is questionable and should be confirmed
                            by someone before order proceeds.
                          </b-checkbox>
                          % endif
                        </div>

                      </div>

                      <br />
                      <div class="field">
                        <b-radio v-model="productIsKnown"
                                 % if not allow_unknown_product:
                                     disabled
                                 % endif
                                 :native-value="false">
                          Product is not yet in the system.
                        </b-radio>
                      </div>

                      <div v-show="!productIsKnown"
                           style="padding-left: 5rem;">

                        <b-field grouped>

                          <b-field label="Brand">
                            <b-input v-model="pendingProduct.brand_name">
                            </b-input>
                          </b-field>

                          <b-field label="Description"
                                   :type="pendingProduct.description ? null : 'is-danger'">
                            <b-input v-model="pendingProduct.description">
                            </b-input>
                          </b-field>

                          <b-field label="Unit Size">
                            <b-input v-model="pendingProduct.size">
                            </b-input>
                          </b-field>

                        </b-field>

                        <b-field grouped>

                          <b-field :label="productKeyLabel">
                            <b-input v-model="pendingProduct[productKeyField]">
                            </b-input>
                          </b-field>

                          <b-field label="Department">
                            <b-select v-model="pendingProduct.department_uuid">
                              <option :value="null">(not known)</option>
                              <option v-for="option in departmentOptions"
                                      :key="option.value"
                                      :value="option.value">
                                {{ option.label }}
                              </option>
                            </b-select>
                          </b-field>

                          <b-field label="Unit Reg. Price">
                            <b-input v-model="pendingProduct.regular_price_amount"
                                     type="number" step="0.01">
                            </b-input>
                          </b-field>

                        </b-field>

                        <b-field grouped>

                          <b-field label="Vendor">
                            <b-input v-model="pendingProduct.vendor_name">
                            </b-input>
                          </b-field>

                          <b-field label="Vendor Item Code">
                            <b-input v-model="pendingProduct.vendor_item_code">
                            </b-input>
                          </b-field>

                          <b-field label="Unit Cost">
                            <b-input v-model="pendingProduct.unit_cost"
                                     type="number" step="0.01"
                                     style="width: 10rem;">
                            </b-input>
                          </b-field>

                          <b-field label="Case Size">
                            <b-input v-model="pendingProduct.case_size"
                                     type="number" step="0.01"
                                     style="width: 7rem;">
                            </b-input>
                          </b-field>

                        </b-field>

                        <b-field label="Notes">
                          <b-input v-model="pendingProduct.notes"
                                   type="textarea">
                          </b-input>
                        </b-field>

                      </div>
                    </b-tab-item>
                    <b-tab-item label="Quantity">

                      <div class="is-pulled-right has-text-centered">
                        <img :src="productImageURL"
                             style="height: 150px; width: 150px; "/>
                      </div>

                      <b-field grouped>
                        <b-field label="Product" horizontal>
                          <span :class="productIsKnown ? null : 'has-text-success'">
                            {{ productIsKnown ? productDisplay : pendingProduct.brand_name + ' ' + pendingProduct.description + ' ' + pendingProduct.size }}
                          </span>
                        </b-field>
                      </b-field>

                      <b-field grouped>

                        <b-field label="Unit Size">
                          <span :class="productIsKnown ? null : 'has-text-success'">
                            {{ productIsKnown ? productSize : pendingProduct.size }}
                          </span>
                        </b-field>

                        <b-field label="Reg. Price"
                                 v-if="productSalePriceDisplay">
                          <span>
                            {{ productUnitRegularPriceDisplay }}
                          </span>
                        </b-field>

                        <b-field label="Unit Price"
                                 v-if="!productSalePriceDisplay">
                          <span :class="productIsKnown ? null : 'has-text-success'"
                                % if product_price_may_be_questionable:
                                    :class="productPriceNeedsConfirmation ? 'has-background-warning' : ''"
                                % endif
                                >
                            {{ productIsKnown ? productUnitPriceDisplay : '$' + pendingProduct.regular_price_amount }}
                          </span>
                        </b-field>

                        <b-field label="Sale Price"
                                 v-if="productSalePriceDisplay">
                          <span class="has-background-warning"
                                :class="productIsKnown ? null : 'has-text-success'">
                            {{ productSalePriceDisplay }}
                          </span>
                        </b-field>

                        <b-field label="Sale Ends"
                                 v-if="productSaleEndsDisplay">
                          <span class="has-background-warning"
                                :class="productIsKnown ? null : 'has-text-success'">
                            {{ productSaleEndsDisplay }}
                          </span>
                        </b-field>

                        <b-field label="Case Size">
                          <span :class="productIsKnown ? null : 'has-text-success'">
                            {{ productIsKnown ? productCaseQuantity : pendingProduct.case_size }}
                          </span>
                        </b-field>

                        <b-field label="Case Price">
                          <span
                                % if product_price_may_be_questionable:
                                    :class="{'has-text-success': !productIsKnown, 'has-background-warning': productPriceNeedsConfirmation || productSalePriceDisplay}"
                                % else:
                                    :class="{'has-text-success': !productIsKnown, 'has-background-warning': !!productSalePriceDisplay}"
                                % endif
                                >
                            {{ getCasePriceDisplay() }}
                          </span>
                        </b-field>

                      </b-field>

                      <b-field grouped>

                        <b-field label="Quantity" horizontal>
                          <numeric-input v-model="productQuantity">
                          </numeric-input>
                        </b-field>

                        <b-select v-model="productUOM">
                          <option v-for="choice in productUnitChoices"
                                  :key="choice.key"
                                  :value="choice.key"
                                  v-html="choice.value">
                          </option>
                        </b-select>

                      </b-field>

                      <b-field grouped>
                        <b-field label="Total Price">
                          <span :class="productSalePriceDisplay ? 'has-background-warning': null">
                            {{ getItemTotalPriceDisplay() }}
                          </span>
                        </b-field>
                      </b-field>

                    </b-tab-item>
                  </b-tabs>

                  <div class="buttons">
                    <b-button @click="showingItemDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              @click="itemDialogSave()"
                              :disabled="itemDialogSaveDisabled"
                              icon-pack="fas"
                              icon-left="save">
                      {{ itemDialogSaveButtonText }}
                    </b-button>
                  </div>

                </div>
              </div>
            </b-modal>

            <tailbone-product-lookup ref="productLookup"
                                     @canceled="productLookupCanceled"
                                     @selected="productLookupSelected">
            </tailbone-product-lookup>

            <b-modal :active.sync="pastItemsShowDialog">
              <div class="card">
                <div class="card-content">

                  <b-table :data="pastItems"
                           icon-pack="fas"
                           :loading="pastItemsLoading"
                           :selected.sync="pastItemsSelected"
                           sortable
                           paginated
                           per-page="5"
                           :debounce-search="1000">
                    <template slot-scope="props">

                      <b-table-column :label="productKeyLabel"
                                      field="key"
                                      sortable>
                        {{ props.row.key }}
                      </b-table-column>

                      <b-table-column label="Brand"
                                      field="brand_name"
                                      sortable
                                      searchable>
                        {{ props.row.brand_name }}
                      </b-table-column>

                      <b-table-column label="Description"
                                      field="description"
                                      sortable
                                      searchable>
                        {{ props.row.description }}
                        {{ props.row.size }}
                      </b-table-column>

                      <b-table-column label="Unit Price"
                                      field="unit_price"
                                      sortable>
                        {{ props.row.unit_price_display }}
                      </b-table-column>

                      <b-table-column label="Sale Price"
                                      field="sale_price"
                                      sortable>
                        <span class="has-background-warning">
                          {{ props.row.sale_price_display }}
                        </span>
                      </b-table-column>

                      <b-table-column label="Sale Ends"
                                      field="sale_ends"
                                      sortable>
                        <span class="has-background-warning">
                          {{ props.row.sale_ends_display }}
                        </span>
                      </b-table-column>

                      <b-table-column label="Department"
                                      field="department_name"
                                      sortable
                                      searchable>
                        {{ props.row.department_name }}
                      </b-table-column>

                      <b-table-column label="Vendor"
                                      field="vendor_name"
                                      sortable
                                      searchable>
                        {{ props.row.vendor_name }}
                      </b-table-column>

                    </template>
                    <template slot="empty">
                      <div class="content has-text-grey has-text-centered">
                        <p>
                          <b-icon
                            pack="fas"
                            icon="fas fa-sad-tear"
                            size="is-large">
                          </b-icon>
                        </p>
                        <p>Nothing here.</p>
                      </div>
                    </template>
                  </b-table>

                  <div class="buttons">
                    <b-button @click="pastItemsShowDialog = false">
                      Cancel
                    </b-button>
                    <b-button type="is-primary"
                              icon-pack="fas"
                              icon-left="plus"
                              @click="pastItemsAddSelected()"
                              :disabled="!pastItemsSelected">
                      Add Selected Item
                    </b-button>
                  </div>

                </div>
              </div>
            </b-modal>

            <b-table v-if="items.length"
                     :data="items"
                     :row-class="(row, i) => row.product_uuid ? null : 'has-text-success'">
              <template slot-scope="props">

                <b-table-column :label="productKeyLabel">
                  {{ props.row.product_key }}
                </b-table-column>

                <b-table-column label="Brand">
                  {{ props.row.product_brand }}
                </b-table-column>

                <b-table-column label="Description">
                  {{ props.row.product_description }}
                </b-table-column>

                <b-table-column label="Size">
                  {{ props.row.product_size }}
                </b-table-column>

                <b-table-column label="Department">
                  {{ props.row.department_display }}
                </b-table-column>

                <b-table-column label="Quantity">
                  <span v-html="props.row.order_quantity_display"></span>
                </b-table-column>

                <b-table-column label="Unit Price">
                  <span
                    % if product_price_may_be_questionable:
                    :class="props.row.price_needs_confirmation ? 'has-background-warning' : ''"
                    % else:
                    :class="props.row.pricing_reflects_sale ? 'has-background-warning' : null"
                    % endif
                    >
                    {{ props.row.unit_price_display }}
                  </span>
                </b-table-column>

                <b-table-column label="Total">
                  <span
                    % if product_price_may_be_questionable:
                    :class="props.row.price_needs_confirmation ? 'has-background-warning' : ''"
                    % else:
                    :class="props.row.pricing_reflects_sale ? 'has-background-warning' : null"
                    % endif
                    >
                    {{ props.row.total_price_display }}
                  </span>
                </b-table-column>

                <b-table-column label="Vendor">
                  {{ props.row.vendor_display }}
                </b-table-column>

                <b-table-column field="actions" label="Actions">
                  <a href="#" class="grid-action"
                     @click.prevent="showEditItemDialog(props.row)">
                    <i class="fas fa-edit"></i>
                    Edit
                  </a>
                  &nbsp;

                  <a href="#" class="grid-action has-text-danger"
                     @click.prevent="deleteItem(props.index)">
                    <i class="fas fa-trash"></i>
                    Delete
                  </a>
                  &nbsp;
                </b-table-column>

              </template>
            </b-table>
          </div>
        </div>
      </b-collapse>

      ${self.order_form_buttons()}

      ${h.form(request.current_route_url(), ref='batchActionForm')}
      ${h.csrf_token(request)}
      ${h.hidden('action', **{'v-model': 'batchAction'})}
      ${h.end_form()}

    </div>
  </script>
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  ${product_lookup.tailbone_product_lookup_component()}
  <script type="text/javascript">

    const CustomerOrderCreator = {
        template: '#customer-order-creator-template',
        data() {

            let defaultUnitChoices = ${json.dumps(default_uom_choices)|n}
            let defaultUOM = ${json.dumps(default_uom)|n}

            return {
                batchAction: null,
                batchTotalPriceDisplay: ${json.dumps(normalized_batch['total_price_display'])|n},

                customerPanelOpen: false,
                contactIsKnown: ${json.dumps(contact_is_known)|n},
                % if new_order_requires_customer:
                contactUUID: ${json.dumps(batch.customer_uuid)|n},
                % else:
                contactUUID: ${json.dumps(batch.person_uuid)|n},
                % endif
                contactDisplay: ${json.dumps(contact_display)|n},
                customerEntry: null,
                contactProfileURL: ${json.dumps(contact_profile_url)|n},
                refreshingContact: false,

                orderPhoneNumber: ${json.dumps(batch.phone_number)|n},
                contactPhones: ${json.dumps(contact_phones)|n},
                addOtherPhoneNumber: ${json.dumps(add_phone_number)|n},

                orderEmailAddress: ${json.dumps(batch.email_address)|n},
                contactEmails: ${json.dumps(contact_emails)|n},
                addOtherEmailAddress: ${json.dumps(add_email_address)|n},

                % if allow_contact_info_choice:

                    editPhoneNumberShowDialog: false,
                    editPhoneNumberOther: null,
                    editPhoneNumberAddOther: false,
                    existingPhoneUUID: null,
                    editPhoneNumberSaving: false,

                    editEmailAddressShowDialog: false,
                    editEmailAddressOther: null,
                    editEmailAddressAddOther: false,
                    existingEmailUUID: null,
                    editEmailAddressOther: null,
                    editEmailAddressSaving: false,

                % endif

                newCustomerFirstName: ${json.dumps(new_customer_first_name)|n},
                newCustomerLastName: ${json.dumps(new_customer_last_name)|n},
                newCustomerPhone: ${json.dumps(new_customer_phone)|n},
                newCustomerEmail: ${json.dumps(new_customer_email)|n},
                contactNotes: ${json.dumps(contact_notes)|n},

                editNewCustomerShowDialog: false,
                editNewCustomerFirstName: null,
                editNewCustomerLastName: null,
                editNewCustomerPhone: null,
                editNewCustomerEmail: null,
                editNewCustomerSaving: false,

                items: ${json.dumps(order_items)|n},
                editingItem: null,
                showingItemDialog: false,
                itemDialogTabIndex: 0,
                pastItemsShowDialog: false,
                pastItemsLoading: false,
                pastItems: [],
                pastItemsSelected: null,
                productIsKnown: true,
                productUUID: null,
                productDisplay: null,
                productKey: null,
                productKeyField: ${json.dumps(product_key_field)|n},
                productKeyLabel: ${json.dumps(product_key_label)|n},
                productSize: null,
                productCaseQuantity: null,
                productUnitPrice: null,
                productUnitPriceDisplay: null,
                productUnitRegularPriceDisplay: null,
                productCasePrice: null,
                productCasePriceDisplay: null,
                productSalePrice: null,
                productSalePriceDisplay: null,
                productSaleEndsDisplay: null,
                productURL: null,
                productImageURL: null,
                productQuantity: null,
                defaultUnitChoices: defaultUnitChoices,
                productUnitChoices: defaultUnitChoices,
                defaultUOM: defaultUOM,
                productUOM: defaultUOM,
                productCaseSize: null,

                % if product_price_may_be_questionable:
                productPriceNeedsConfirmation: false,
                % endif

                pendingProduct: {},
                departmentOptions: ${json.dumps(department_options)|n},

                ## TODO: should find a better way to handle CSRF token
                csrftoken: ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n},

                submittingOrder: false,
            }
        },
        computed: {
            customerPanelHeader() {
                let text = "Customer"

                if (this.contactIsKnown) {
                    if (this.contactUUID) {
                        if (this.$refs.contactAutocomplete) {
                            text = "Customer: " + this.$refs.contactAutocomplete.getDisplayText()
                        } else {
                            text = "Customer: " + this.contactDisplay
                        }
                    }
                } else {
                    if (this.contactDisplay) {
                        text = "Customer: " + this.contactDisplay
                    }
                }

                if (!this.customerPanelOpen) {
                    text += ' <p class="' + this.customerHeaderClass + '" style="display: inline-block; float: right;">' + this.customerStatusText + '</p>'
                }

                return text
            },
            customerHeaderClass() {
                if (!this.customerPanelOpen) {
                    if (this.customerStatusType == 'is-danger') {
                        return 'has-text-danger'
                    } else if (this.customerStatusType == 'is-warning') {
                        return 'has-text-warning'
                    }
                }
            },
            customerPanelType() {
                if (!this.customerPanelOpen) {
                    return this.customerStatusType
                }
            },
            customerStatusType() {
                return this.customerStatusTypeAndText.type
            },
            customerStatusText() {
                return this.customerStatusTypeAndText.text
            },
            customerStatusTypeAndText() {
                let phoneNumber = null
                if (this.contactIsKnown) {
                    if (!this.contactUUID) {
                        return {
                            type: 'is-danger',
                            text: "Please identify the customer.",
                        }
                    }
                    if (!this.orderPhoneNumber) {
                        return {
                            type: 'is-warning',
                            text: "Please provide a phone number for the customer.",
                        }
                    }
                    if (this.contactNotes.length) {
                        return {
                            type: 'is-warning',
                            text: "Please review notes below.",
                        }
                    }
                    phoneNumber = this.orderPhoneNumber
                } else { // customer is not known
                    if (!this.contactDisplay) {
                        return {
                            type: 'is-danger',
                            text: "Please identify the customer.",
                        }
                    }
                    if (!this.newCustomerPhone) {
                        return {
                            type: 'is-warning',
                            text: "Please provide a phone number for the customer.",
                        }
                    }
                    phoneNumber = this.newCustomerPhone
                }

                let phoneDigits = phoneNumber.replace(/\D/g, '')
                if (!phoneDigits.length || (phoneDigits.length != 7 && phoneDigits.length != 10)) {
                    return {
                        type: 'is-warning',
                        text: "The phone number does not appear to be valid.",
                    }
                }

                if (!this.contactIsKnown) {
                    return {
                        type: 'is-warning',
                        text: "Will create a new customer record.",
                    }
                }

                return {
                    type: null,
                    text: "Customer info looks okay.",
                }
            },

            % if allow_contact_info_choice:

                editPhoneNumberSaveDisabled() {
                    if (this.editPhoneNumberSaving) {
                        return true
                    }
                    if (!this.existingPhoneUUID && !this.editPhoneNumberOther) {
                        return true
                    }
                    return false
                },

                editPhoneNumberSaveText() {
                    if (this.editPhoneNumberSaving) {
                        return "Working, please wait..."
                    }
                    return "Save"
                },

                editEmailAddressSaveDisabled() {
                    if (this.editEmailAddressSaving) {
                        return true
                    }
                    if (!this.existingEmailUUID && !this.editEmailAddressOther) {
                        return true
                    }
                    return false
                },

                editEmailAddressSaveText() {
                    if (this.editEmailAddressSaving) {
                        return "Working, please wait..."
                    }
                    return "Save"
                },

            % endif

            editNewCustomerSaveDisabled() {
                if (this.editNewCustomerSaving) {
                    return true
                }
                if (!(this.editNewCustomerFirstName && this.editNewCustomerLastName)) {
                    return true
                }
                if (!(this.editNewCustomerPhone || this.editNewCustomerEmail)) {
                    return true
                }
                return false
            },

            editNewCustomerSaveText() {
                if (this.editNewCustomerSaving) {
                    return "Working, please wait..."
                }
                return "Save"
            },

            itemsPanelHeader() {
                let text = "Items"

                if (this.items.length) {
                    text = "Items: " + this.items.length.toString() + " for " + this.batchTotalPriceDisplay
                }

                return text
            },

            itemDialogSaveDisabled() {
                if (this.productIsKnown) {
                    if (!this.productUUID) {
                        return true
                    }
                } else {
                    if (!this.pendingProduct.description) {
                        return true
                    }
                }
                if (!this.productUOM) {
                    return true
                }
                return false
            },

            itemDialogSaveButtonText() {
                return this.editingItem ? "Update Item" : "Add Item"
            },

            submitOrderButtonText() {
                if (this.submittingOrder) {
                    return "Working, please wait..."
                }
                return "Submit this Order"
            },
        },
        mounted() {
            if (this.customerStatusType) {
                this.customerPanelOpen = true
            }
        },
        watch: {

            contactIsKnown: function(val) {

                // when user clicks "contact is known" then we want to
                // set focus to the autocomplete component
                if (val) {
                    this.$nextTick(() => {
                        this.$refs.contactAutocomplete.focus()
                    })

                // if user has already specified a proper contact,
                // i.e.  `contactUUID` is not null, *and* user has
                // clicked the "contact is not yet in the system"
                // button, i.e. `val` is false, then we want to *clear
                // out* the existing contact selection.  this is
                // primarily to avoid any ambiguity.
                } else if (this.contactUUID) {
                    this.$refs.contactAutocomplete.clearSelection()
                }
            },
        },
        methods: {

            startOverEntirely() {
                let msg = "Are you sure you want to start over entirely?\n\n"
                    + "This will totally delete this order and start a new one."
                if (!confirm(msg)) {
                    return
                }
                this.batchAction = 'start_over_entirely'
                this.$nextTick(function() {
                    this.$refs.batchActionForm.submit()
                })
            },

            // startOverCustomer(confirmed) {
            //     if (!confirmed) {
            //         let msg = "Are you sure you want to start over for the customer data?"
            //         if (!confirm(msg)) {
            //             return
            //         }
            //     }
            //     this.contactIsKnown = true
            //     this.contactUUID = null
            //     // this.customerEntry = null
            //     this.phoneNumberEntry = null
            //     this.customerName = null
            //     this.phoneNumber = null
            // },

            // startOverItem(confirmed) {
            //     if (!confirmed) {
            //         let msg = "Are you sure you want to start over for the item data?"
            //         if (!confirm(msg)) {
            //             return
            //         }
            //     }
            //     // TODO: reset things
            // },

            cancelOrder() {
                let msg = "Are you sure you want to cancel?\n\n"
                    + "This will totally delete the current order."
                if (!confirm(msg)) {
                    return
                }
                this.batchAction = 'delete_batch'
                this.$nextTick(function() {
                    this.$refs.batchActionForm.submit()
                })
            },

            submitBatchData(params, success, failure) {
                let url = ${json.dumps(request.current_route_url())|n}
                
                let headers = {
                    ## TODO: should find a better way to handle CSRF token
                    'X-CSRF-TOKEN': this.csrftoken,
                }

                ## TODO: should find a better way to handle CSRF token
                this.$http.post(url, params, {headers: headers}).then((response) => {
                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: response.data.error,
                            type: 'is-danger',
                            duration: 2000, // 2 seconds
                        })
                        if (failure) {
                            failure(response)
                        }
                    } else if (success) {
                        success(response)
                    }
                }, response => {
                    this.$buefy.toast.open({
                        message: "Unexpected error occurred",
                        type: 'is-danger',
                        duration: 2000, // 2 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })
            },

            submitOrder() {
                this.submittingOrder = true

                let params = {
                    action: 'submit_new_order',
                }

                this.submitBatchData(params, response => {
                    if (response.data.next_url) {
                        location.href = response.data.next_url
                    } else {
                        location.reload()
                    }
                }, response => {
                    this.submittingOrder = false
                })
            },

            contactChanged(uuid, callback) {

                // clear out the past items cache
                this.pastItemsSelected = null
                this.pastItems = []

                let params
                if (!uuid) {
                    params = {
                        action: 'unassign_contact',
                    }
                } else {
                    params = {
                        action: 'assign_contact',
                        uuid: this.contactUUID,
                    }
                }
                let that = this
                this.submitBatchData(params, function(response) {
                    % if new_order_requires_customer:
                    that.contactUUID = response.data.customer_uuid
                    % else:
                    that.contactUUID = response.data.person_uuid
                    % endif
                    that.contactDisplay = response.data.contact_display
                    that.orderPhoneNumber = response.data.phone_number
                    that.orderEmailAddress = response.data.email_address
                    that.addOtherPhoneNumber = response.data.add_phone_number
                    that.addOtherEmailAddress = response.data.add_email_address
                    that.contactProfileURL = response.data.contact_profile_url
                    that.contactPhones = response.data.contact_phones
                    that.contactEmails = response.data.contact_emails
                    that.contactNotes = response.data.contact_notes
                    if (callback) {
                        callback()
                    }
                })
            },

            refreshContact() {
                this.refreshingContact = true
                this.contactChanged(this.contactUUID, () => {
                    this.refreshingContact = false
                    this.$buefy.toast.open({
                        message: "Contact info has been refreshed.",
                        type: 'is-success',
                        duration: 3000, // 3 seconds
                    })
                })
            },

            % if allow_contact_info_choice:

                editPhoneNumberInit() {
                    this.existingPhoneUUID = null
                    let normalOrderPhone = (this.orderPhoneNumber || '').replace(/\D/g, '')
                    for (let phone of this.contactPhones) {
                        let normal = phone.number.replace(/\D/g, '')
                        if (normal == normalOrderPhone) {
                            this.existingPhoneUUID = phone.uuid
                            break
                        }
                    }
                    this.editPhoneNumberOther = this.existingPhoneUUID ? null : this.orderPhoneNumber
                    this.editPhoneNumberAddOther = this.addOtherPhoneNumber
                    this.editPhoneNumberShowDialog = true
                },

                editPhoneNumberSave() {
                    this.editPhoneNumberSaving = true

                    let params = {
                        action: 'update_phone_number',
                        phone_number: null,
                    }

                    if (this.existingPhoneUUID) {
                        for (let phone of this.contactPhones) {
                            if (phone.uuid == this.existingPhoneUUID) {
                                params.phone_number = phone.number
                                break
                            }
                        }
                    }

                    if (params.phone_number) {
                        params.add_phone_number = false
                    } else {
                        params.phone_number = this.editPhoneNumberOther
                        params.add_phone_number = this.editPhoneNumberAddOther
                    }

                    this.submitBatchData(params, response => {
                        if (response.data.success) {
                            this.orderPhoneNumber = response.data.phone_number
                            this.addOtherPhoneNumber = response.data.add_phone_number
                            this.editPhoneNumberShowDialog = false
                        } else {
                            this.$buefy.toast.open({
                                message: "Save failed: " + response.data.error,
                                type: 'is-danger',
                                duration: 2000, // 2 seconds
                            })
                        }
                        this.editPhoneNumberSaving = false
                    })

                },

                editEmailAddressInit() {
                    this.existingEmailUUID = null
                    let normalOrderEmail = (this.orderEmailAddress || '').toLowerCase()
                    for (let email of this.contactEmails) {
                        let normal = email.address.toLowerCase()
                        if (normal == normalOrderEmail) {
                            this.existingEmailUUID = email.uuid
                            break
                        }
                    }
                    this.editEmailAddressOther = this.existingEmailUUID ? null : this.orderEmailAddress
                    this.editEmailAddressAddOther = this.addOtherEmailAddress
                    this.editEmailAddressShowDialog = true
                },

                editEmailAddressSave() {
                    this.editEmailAddressSaving = true

                    let params = {
                        action: 'update_email_address',
                        email_address: null,
                    }

                    if (this.existingEmailUUID) {
                        for (let email of this.contactEmails) {
                            if (email.uuid == this.existingEmailUUID) {
                                params.email_address = email.address
                                break
                            }
                        }
                    }

                    if (params.email_address) {
                        params.add_email_address = false
                    } else {
                        params.email_address = this.editEmailAddressOther
                        params.add_email_address = this.editEmailAddressAddOther
                    }

                    this.submitBatchData(params, response => {
                        if (response.data.success) {
                            this.orderEmailAddress = response.data.email_address
                            this.addOtherEmailAddress = response.data.add_email_address
                            this.editEmailAddressShowDialog = false
                        } else {
                            this.$buefy.toast.open({
                                message: "Save failed: " + response.data.error,
                                type: 'is-danger',
                                duration: 2000, // 2 seconds
                            })
                        }
                        this.editEmailAddressSaving = false
                    })
                },

            % endif

            editNewCustomerInit() {
                this.editNewCustomerFirstName = this.newCustomerFirstName
                this.editNewCustomerLastName = this.newCustomerLastName
                this.editNewCustomerPhone = this.newCustomerPhone
                this.editNewCustomerEmail = this.newCustomerEmail
                this.editNewCustomerShowDialog = true
                this.$nextTick(() => {
                    this.$refs.editNewCustomerInput.focus()
                })
            },

            editNewCustomerSave() {
                this.editNewCustomerSaving = true

                let params = {
                    action: 'update_pending_customer',
                    first_name: this.editNewCustomerFirstName,
                    last_name: this.editNewCustomerLastName,
                    phone_number: this.editNewCustomerPhone,
                    email_address: this.editNewCustomerEmail,
                }

                this.submitBatchData(params, response => {
                    if (response.data.success) {
                        this.contactDisplay = response.data.new_customer_name
                        this.newCustomerFirstName = response.data.new_customer_first_name
                        this.newCustomerLastName = response.data.new_customer_last_name
                        this.newCustomerPhone = response.data.phone_number
                        this.orderPhoneNumber = response.data.phone_number
                        this.newCustomerEmail = response.data.email_address
                        this.orderEmailAddress = response.data.email_address
                        this.editNewCustomerShowDialog = false
                    } else {
                        this.$buefy.toast.open({
                            message: "Save failed: " + (response.data.error || "(unknown error)"),
                            type: 'is-danger',
                            duration: 2000, // 2 seconds
                        })
                    }
                    this.editNewCustomerSaving = false
                })

            },

            getCasePriceDisplay() {
                if (this.productIsKnown) {
                    return this.productCasePriceDisplay
                }

                let casePrice = this.getItemCasePrice()
                if (casePrice) {
                    return "$" + casePrice
                }
            },

            getItemUnitPrice() {
                if (this.productIsKnown) {
                    return this.productSalePrice || this.productUnitPrice
                }
                return this.pendingProduct.regular_price_amount
            },

            getItemCasePrice() {
                if (this.productIsKnown) {
                    return this.productCasePrice
                }

                if (this.pendingProduct.regular_price_amount) {
                    if (this.pendingProduct.case_size) {
                        let casePrice = this.pendingProduct.regular_price_amount * this.pendingProduct.case_size
                        casePrice = casePrice.toFixed(2)
                        return casePrice
                    }
                }
            },

            getItemTotalPriceDisplay() {
                let basePrice = null
                if (this.productUOM == '${enum.UNIT_OF_MEASURE_CASE}') {
                    basePrice = this.getItemCasePrice()
                } else {
                    basePrice = this.getItemUnitPrice()
                }

                if (basePrice) {
                    let totalPrice = basePrice * this.productQuantity
                    if (totalPrice) {
                        totalPrice = totalPrice.toFixed(2)
                        return "$" + totalPrice
                    }
                }
            },

            productFullLookup() {
                this.showingItemDialog = false
                let term = this.$refs.productAutocomplete.getUserInput()
                this.$refs.productLookup.showDialog(term)
            },

            productLookupCanceled() {
                this.showingItemDialog = true
            },

            productLookupSelected(selected) {
                this.clearProduct()
                this.productChanged(selected.uuid)
                this.showingItemDialog = true
            },

            copyPendingProductAttrs(from, to) {
                to.upc = from.upc
                to.item_id = from.item_id
                to.scancode = from.scancode
                to.brand_name = from.brand_name
                to.description = from.description
                to.size = from.size
                to.department_uuid = from.department_uuid
                to.regular_price_amount = from.regular_price_amount
                to.vendor_name = from.vendor_name
                to.vendor_item_code = from.vendor_item_code
                to.unit_cost = from.unit_cost
                to.case_size = from.case_size
                to.notes = from.notes
            },

            showAddItemDialog() {
                this.customerPanelOpen = false
                this.editingItem = null
                this.productIsKnown = true
                this.productUUID = null
                this.productDisplay = null
                this.productKey = null
                this.productSize = null
                this.productCaseQuantity = null
                this.productUnitPrice = null
                this.productUnitPriceDisplay = null
                this.productUnitRegularPriceDisplay = null
                this.productCasePrice = null
                this.productCasePriceDisplay = null
                this.productSalePrice = null
                this.productSalePriceDisplay = null
                this.productSaleEndsDisplay = null
                this.productImageURL = '${request.static_url('tailbone:static/img/product.png')}'

                this.pendingProduct = {}

                this.productQuantity = 1
                this.productUnitChoices = this.defaultUnitChoices
                this.productUOM = this.defaultUOM

                % if product_price_may_be_questionable:
                this.productPriceNeedsConfirmation = false
                % endif

                this.itemDialogTabIndex = 0
                this.showingItemDialog = true
                this.$nextTick(() => {
                    this.$refs.productAutocomplete.focus()
                })
            },

            showAddPastItem() {
                this.pastItemsSelected = null

                if (!this.pastItems.length) {
                    this.pastItemsLoading = true
                    let params = {
                        action: 'get_past_items',
                    }
                    this.submitBatchData(params, response => {
                        this.pastItems = response.data.past_items
                        this.pastItemsLoading = false
                    })
                }

                this.pastItemsShowDialog = true
            },

            pastItemsAddSelected() {
                this.pastItemsShowDialog = false

                let selected = this.pastItemsSelected
                this.editingItem = null
                this.productIsKnown = true
                this.productUUID = selected.uuid
                this.productDisplay = selected.full_description
                this.productKey = selected.key
                this.productSize = selected.size
                this.productCaseQuantity = selected.case_quantity
                this.productUnitPrice = selected.unit_price
                this.productUnitPriceDisplay = selected.unit_price_display
                this.productUnitRegularPriceDisplay = selected.unit_price_display
                this.productCasePrice = selected.case_price
                this.productCasePriceDisplay = selected.case_price_display
                this.productSalePrice = selected.sale_price
                this.productSalePriceDisplay = selected.sale_price_display
                this.productSaleEndsDisplay = selected.sale_ends_display
                this.productImageURL = selected.image_url
                this.productURL = selected.url
                this.productQuantity = 1
                this.productUnitChoices = selected.uom_choices
                // TODO: seems like the default should not be so generic?
                this.productUOM = this.defaultUOM

                % if product_price_may_be_questionable:
                this.productPriceNeedsConfirmation = false
                % endif

                this.itemDialogTabIndex = 1
                this.showingItemDialog = true
            },

            showEditItemDialog(row) {
                this.editingItem = row

                this.productIsKnown = !!row.product_uuid
                this.productUUID = row.product_uuid
                this.pendingProduct = {}
                if (row.pending_product) {
                    this.copyPendingProductAttrs(row.pending_product,
                                                 this.pendingProduct)
                }

                this.productDisplay = row.product_full_description
                this.productKey = row.product_key
                this.productSize = row.product_size
                this.productCaseQuantity = row.case_quantity
                this.productURL = row.product_url
                this.productUnitPrice = row.unit_price
                this.productUnitPriceDisplay = row.unit_price_display
                this.productUnitRegularPriceDisplay = row.unit_regular_price_display
                this.productCasePrice = row.case_price
                this.productCasePriceDisplay = row.case_price_display
                this.productSalePrice = row.sale_price
                this.productSalePriceDisplay = row.unit_sale_price_display
                this.productSaleEndsDisplay = row.sale_ends_display
                this.productImageURL = row.product_image_url || '${request.static_url('tailbone:static/img/product.png')}'

                % if product_price_may_be_questionable:
                this.productPriceNeedsConfirmation = row.price_needs_confirmation
                % endif

                this.productQuantity = row.order_quantity
                this.productUnitChoices = row.order_uom_choices
                this.productUOM = row.order_uom

                this.itemDialogTabIndex = 1
                this.showingItemDialog = true
            },

            deleteItem(index) {
                if (!confirm("Are you sure you want to delete this item?")) {
                    return
                }

                let params = {
                    action: 'delete_item',
                    uuid: this.items[index].uuid,
                }
                this.submitBatchData(params, response => {
                    if (response.data.error) {
                        this.$buefy.toast.open({
                            message: "Delete failed:  " + response.data.error,
                            type: 'is-warning',
                            duration: 2000, // 2 seconds
                        })
                    } else {
                        this.items.splice(index, 1)
                        this.batchTotalPriceDisplay = response.data.batch.total_price_display
                    }
                })
            },

            clearProduct() {
                this.productUUID = null
                this.productDisplay = null
                this.productKey = null
                this.productSize = null
                this.productCaseQuantity = null
                this.productUnitPrice = null
                this.productUnitPriceDisplay = null
                this.productUnitRegularPriceDisplay = null
                this.productCasePrice = null
                this.productCasePriceDisplay = null
                this.productSalePrice = null
                this.productSalePriceDisplay = null
                this.productSaleEndsDisplay = null
                this.productURL = null
                this.productImageURL = null
                this.productUnitChoices = this.defaultUnitChoices

                % if product_price_may_be_questionable:
                this.productPriceNeedsConfirmation = false
                % endif
            },

            setProductUnitChoices(choices) {
                this.productUnitChoices = choices

                let found = false
                for (let uom of choices) {
                    if (this.productUOM == uom.key) {
                        found = true
                        break
                    }
                }
                if (!found) {
                    this.productUOM = choices[0].key
                }
            },

            productChanged(uuid) {
                if (uuid) {
                    let params = {
                        action: 'get_product_info',
                        uuid: uuid,
                    }
                    // nb. it is possible for the handler to "swap"
                    // the product selection, i.e. user chooses a "per
                    // LB" item but the handler only allows selling by
                    // the "case" item.  so we do not assume the uuid
                    // received above is the correct one, but just use
                    // whatever came back from handler
                    this.submitBatchData(params, response => {
                        this.productUUID = response.data.uuid
                        this.productKey = response.data.key
                        this.productDisplay = response.data.full_description
                        this.productSize = response.data.size
                        this.productCaseQuantity = response.data.case_quantity
                        this.productUnitPrice = response.data.unit_price
                        this.productUnitPriceDisplay = response.data.unit_price_display
                        this.productUnitRegularPriceDisplay = response.data.unit_price_display
                        this.productCasePrice = response.data.case_price
                        this.productCasePriceDisplay = response.data.case_price_display
                        this.productSalePrice = response.data.sale_price
                        this.productSalePriceDisplay = response.data.sale_price_display
                        this.productSaleEndsDisplay = response.data.sale_ends_display
                        this.productURL = response.data.url
                        this.productImageURL = response.data.image_url
                        this.setProductUnitChoices(response.data.uom_choices)

                        % if product_price_may_be_questionable:
                        this.productPriceNeedsConfirmation = false
                        % endif

                        this.itemDialogTabIndex = 1

                    }, response => {
                        this.clearProduct()
                    })
                } else {
                    this.clearProduct()
                }
            },

            itemDialogSave() {

                let params = {
                    product_is_known: this.productIsKnown,
                    % if product_price_may_be_questionable:
                        price_needs_confirmation: this.productPriceNeedsConfirmation,
                    % endif
                    order_quantity: this.productQuantity,
                    order_uom: this.productUOM,
                }

                if (this.productIsKnown) {
                    params.product_uuid = this.productUUID
                } else {
                    params.pending_product = this.pendingProduct
                }

                if (this.editingItem) {
                    params.action = 'update_item'
                    params.uuid = this.editingItem.uuid
                } else {
                    params.action = 'add_item'
                }

                this.submitBatchData(params, response => {

                    if (params.action == 'add_item') {
                        this.items.push(response.data.row)

                    } else { // update_item
                        // must update each value separately, instead of
                        // overwriting the item record, or else display will
                        // not update properly
                        for (let [key, value] of Object.entries(response.data.row)) {
                            this.editingItem[key] = value
                        }
                    }

                    // also update the batch total price
                    this.batchTotalPriceDisplay = response.data.batch.total_price_display

                    this.showingItemDialog = false
                })
            },
        },
    }

    Vue.component('customer-order-creator', CustomerOrderCreator)

  </script>
</%def>


${parent.body()}
