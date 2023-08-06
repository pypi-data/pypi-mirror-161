## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if instance.custorder_item_records:
      <nav class="panel">
        <p class="panel-heading">Cross-Reference</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column;">
            <p class="block">
              This ${model_title} is referenced by the following<br />
              Customer Order Items:
            </p>
            <ul class="list">
              % for item in instance.custorder_item_records:
                  <li class="list-item">
                    ${h.link_to('#{}-{}'.format(item.order.id, item.sequence), url('custorders.items.view', uuid=item.uuid))}
                  </li>
              % endfor
            </ul>
          </div>
        </div>
      </nav>
  % endif

  % if instance.status_code == enum.PENDING_PRODUCT_STATUS_PENDING and master.has_perm('resolve_product'):
      <nav class="panel">
        <p class="panel-heading">Tools</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column;">
            <div class="buttons">
              <b-button type="is-primary"
                        @click="resolveProductInit()"
                        icon-pack="fas"
                        icon-left="object-ungroup">
                Resolve Product
              </b-button>
            </div>
          </div>
        </div>
      </nav>

      <b-modal has-modal-card
               :active.sync="resolveProductShowDialog">
        <div class="modal-card">
          ${h.form(url('{}.resolve_product'.format(route_prefix), uuid=instance.uuid), ref='resolveProductForm')}
          ${h.csrf_token(request)}

          <header class="modal-card-head">
            <p class="modal-card-title">Resolve Product</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              If this Product already exists, you can declare that by
              identifying the record below.
            </p>
            <p class="block">
              The app will take care of updating any Customer Orders
              etc.  as needed once you declare the match.
            </p>
            <b-field grouped>
              <b-field label="Pending">
                <span>${instance.full_description}</span>
              </b-field>
              <b-field label="Actual Product" expanded>
                <tailbone-autocomplete name="product_uuid"
                                       v-model="resolveProductUUID"
                                       ref="resolveProductAutocomplete"
                                       service-url="${url('products.autocomplete')}">
                </tailbone-autocomplete>
              </b-field>
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="resolveProductShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      :disabled="resolveProductSubmitDisabled"
                      @click="resolveProductSubmit()"
                      icon-pack="fas"
                      icon-left="object-ungroup">
              {{ resolveProductSubmitting ? "Working, please wait..." : "I declare these are the same" }}
            </b-button>
          </footer>
          ${h.end_form()}
        </div>
      </b-modal>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.resolveProductShowDialog = false
    ThisPageData.resolveProductUUID = null
    ThisPageData.resolveProductSubmitting = false

    ThisPage.computed.resolveProductSubmitDisabled = function() {
        if (this.resolveProductSubmitting) {
            return true
        }
        if (!this.resolveProductUUID) {
            return true
        }
        return false
    }

    ThisPage.methods.resolveProductInit = function() {
        this.resolveProductUUID = null
        this.resolveProductShowDialog = true
        this.$nextTick(() => {
            this.$refs.resolveProductAutocomplete.focus()
        })
    }

    ThisPage.methods.resolveProductSubmit = function() {
        this.resolveProductSubmitting = true
        this.$refs.resolveProductForm.submit()
    }

  </script>
</%def>


${parent.body()}
