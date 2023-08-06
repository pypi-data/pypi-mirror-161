## -*- coding: utf-8; -*-

<%def name="tailbone_product_lookup_template()">
  <script type="text/x-template" id="tailbone-product-lookup-template">
    <div>
      <b-modal :active.sync="showingDialog">
        <div class="card">
          <div class="card-content">

            <b-field grouped>

              <b-input v-model="searchTerm" 
                       ref="searchTermInput"
                       @keydown.native="searchTermInputKeydown">
              </b-input>

              <b-button class="control"
                        type="is-primary"
                        @click="performSearch()">
                Search
              </b-button>

              <b-checkbox v-model="searchProductKey"
                          native-value="true">
                ${request.rattail_config.product_key_title()}
              </b-checkbox>

              <b-checkbox v-model="searchVendorItemCode"
                          native-value="true">
                Vendor Code
              </b-checkbox>

              <b-checkbox v-model="searchAlternateCode"
                          native-value="true">
                Alt Code
              </b-checkbox>

              <b-checkbox v-model="searchProductBrand"
                          native-value="true">
                Brand
              </b-checkbox>

              <b-checkbox v-model="searchProductDescription"
                          native-value="true">
                Description
              </b-checkbox>

            </b-field>

            <b-table :data="searchResults"
                     narrowed
                     icon-pack="fas"
                     :loading="searchResultsLoading"
                     :selected.sync="searchResultSelected">
              <template slot-scope="props">

                <b-table-column label="${request.rattail_config.product_key_title()}"
                                field="product_key">
                  {{ props.row.product_key }}
                </b-table-column>

                <b-table-column label="Brand"
                                field="brand_name">
                  {{ props.row.brand_name }}
                </b-table-column>

                <b-table-column label="Description"
                                field="description">
                  {{ props.row.description }}
                  {{ props.row.size }}
                </b-table-column>

                <b-table-column label="Unit Price"
                                field="unit_price">
                  {{ props.row.unit_price_display }}
                </b-table-column>

                <b-table-column label="Sale Price"
                                field="sale_price">
                  <span class="has-background-warning">
                    {{ props.row.sale_price_display }}
                  </span>
                </b-table-column>

                <b-table-column label="Sale Ends"
                                field="sale_ends">
                  <span class="has-background-warning">
                    {{ props.row.sale_ends_display }}
                  </span>
                </b-table-column>

                <b-table-column label="Department"
                                field="department_name">
                  {{ props.row.department_name }}
                </b-table-column>

                <b-table-column label="Vendor"
                                field="vendor_name">
                  {{ props.row.vendor_name }}
                </b-table-column>

                <b-table-column label="Actions">
                  <a :href="props.row.url"
                     target="_blank"
                     class="grid-action">
                    <i class="fas fa-external-link-alt"></i>
                    View
                  </a>
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

            <br />
            <div class="level">
              <div class="level-left">
                <div class="level-item buttons">
                  <b-button @click="cancelDialog()">
                    Cancel
                  </b-button>
                  <b-button type="is-primary"
                            @click="selectResult()"
                            :disabled="!searchResultSelected">
                    Choose Selected
                  </b-button>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span v-if="searchResultsElided"
                        class="has-text-danger">
                    {{ searchResultsElided }} results are not shown
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </b-modal>
    </div>
  </script>
</%def>

<%def name="tailbone_product_lookup_component()">
  <script type="text/javascript">

    const TailboneProductLookup = {
        template: '#tailbone-product-lookup-template',
        data() {
            return {
                showingDialog: false,

                searchTerm: null,
                searchTermLastUsed: null,

                searchProductKey: true,
                searchVendorItemCode: true,
                searchProductBrand: true,
                searchProductDescription: true,
                searchAlternateCode: true,

                searchResults: [],
                searchResultsLoading: false,
                searchResultsElided: 0,
                searchResultSelected: null,
            }
        },
        methods: {

            showDialog(term) {

                this.searchResultSelected = null

                if (term !== undefined) {
                    this.searchTerm = term
                    // perform search if invoked with new term
                    if (term != this.searchTermLastUsed) {
                        this.searchTermLastUsed = null
                        this.performSearch()
                    }
                } else {
                    this.searchTerm = this.searchTermLastUsed
                }

                this.showingDialog = true
                this.$nextTick(() => {
                    this.$refs.searchTermInput.focus()
                })
            },

            searchTermInputKeydown(event) {
                if (event.which == 13) {
                    this.performSearch()
                }
            },

            cancelDialog() {
                this.searchResultSelected = null
                this.showingDialog = false
                this.$emit('canceled')
            },

            selectResult() {
                this.showingDialog = false
                this.$emit('selected', this.searchResultSelected)
            },

            performSearch() {
                if (this.searchResultsLoading) {
                    return
                }

                if (!this.searchTerm || !this.searchTerm.length) {
                    this.$refs.searchTermInput.focus()
                    return
                }

                this.searchResultsLoading = true
                this.searchResultSelected = null

                let url = '${url('products.search')}'
                let params = {
                    term: this.searchTerm,
                    search_product_key: this.searchProductKey,
                    search_vendor_code: this.searchVendorItemCode,
                    search_brand_name: this.searchProductBrand,
                    search_description: this.searchProductDescription,
                    search_alt_code: this.searchAlternateCode,
                }

                this.$http.get(url, {params: params}).then((response) => {
                    this.searchTermLastUsed = params.term
                    this.searchResults = response.data.results
                    this.searchResultsElided = response.data.elided
                    this.searchResultsLoading = false
                })
            },
        },
    }

    Vue.component('tailbone-product-lookup', TailboneProductLookup)

  </script>
</%def>
