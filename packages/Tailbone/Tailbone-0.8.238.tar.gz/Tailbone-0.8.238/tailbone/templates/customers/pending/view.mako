## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
## <%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="object_helpers()">
  ${parent.object_helpers()}

  % if instance.custorder_records:
      <nav class="panel">
        <p class="panel-heading">Cross-Reference</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column;">
            <p class="block">
              This ${model_title} is referenced by the following<br />
              Customer Orders:
            </p>
            <ul class="list">
              % for order in instance.custorder_records:
                  <li class="list-item">
                    ${h.link_to(order, url('custorders.view', uuid=order.uuid))}
                  </li>
              % endfor
            </ul>
          </div>
        </div>
      </nav>
  % endif

  ## % if instance.status_code == enum.PENDING_CUSTOMER_STATUS_PENDING and master.has_any_perm('resolve_person', 'resolve_customer'):
  % if instance.status_code == enum.PENDING_CUSTOMER_STATUS_PENDING and master.has_perm('resolve_person'):
      <nav class="panel">
        <p class="panel-heading">Tools</p>
        <div class="panel-block">
          <div style="display: flex; flex-direction: column;">
            % if master.has_perm('resolve_person'):
                <div class="buttons">
                  <b-button type="is-primary"
                            @click="resolvePersonInit()"
                            icon-pack="fas"
                            icon-left="object-ungroup">
                    Resolve Person
                  </b-button>
                </div>
            % endif
##             % if master.has_perm('resolve_customer'):
##                 <div class="buttons">
##                   <b-button type="is-primary"
##                             icon-pack="fas"
##                             icon-left="object-ungroup">
##                     Resolve Customer
##                   </b-button>
##                 </div>
##             % endif
          </div>
        </div>
      </nav>

      <b-modal has-modal-card
               :active.sync="resolvePersonShowDialog">
        <div class="modal-card">
          ${h.form(url('{}.resolve_person'.format(route_prefix), uuid=instance.uuid), ref='resolvePersonForm')}
          ${h.csrf_token(request)}

          <header class="modal-card-head">
            <p class="modal-card-title">Resolve Person</p>
          </header>

          <section class="modal-card-body">
            <p class="block">
              If this Person already exists, you can declare that by
              identifying the record below.
            </p>
            <p class="block">
              The app will take care of updating any Customer Orders
              etc.  as needed once you declare the match.
            </p>
            <b-field grouped>
              <b-field label="Pending">
                <span>${instance.display_name}</span>
              </b-field>
              <b-field label="Actual Person" expanded>
                <tailbone-autocomplete name="person_uuid"
                                       v-model="resolvePersonUUID"
                                       ref="resolvePersonAutocomplete"
                                       service-url="${url('people.autocomplete')}">
                </tailbone-autocomplete>
              </b-field>
            </b-field>
          </section>

          <footer class="modal-card-foot">
            <b-button @click="resolvePersonShowDialog = false">
              Cancel
            </b-button>
            <b-button type="is-primary"
                      :disabled="resolvePersonSubmitDisabled"
                      @click="resolvePersonSubmit()"
                      icon-pack="fas"
                      icon-left="object-ungroup">
              {{ resolvePersonSubmitting ? "Working, please wait..." : "I declare these are the same" }}
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

    ThisPageData.resolvePersonShowDialog = false
    ThisPageData.resolvePersonUUID = null
    ThisPageData.resolvePersonSubmitting = false

    ThisPage.computed.resolvePersonSubmitDisabled = function() {
        if (this.resolvePersonSubmitting) {
            return true
        }
        if (!this.resolvePersonUUID) {
            return true
        }
        return false
    }

    ThisPage.methods.resolvePersonInit = function() {
        this.resolvePersonUUID = null
        this.resolvePersonShowDialog = true
        this.$nextTick(() => {
            this.$refs.resolvePersonAutocomplete.focus()
        })
    }

    ThisPage.methods.resolvePersonSubmit = function() {
        this.resolvePersonSubmitting = true
        this.$refs.resolvePersonForm.submit()
    }

  </script>
</%def>

${parent.body()}
