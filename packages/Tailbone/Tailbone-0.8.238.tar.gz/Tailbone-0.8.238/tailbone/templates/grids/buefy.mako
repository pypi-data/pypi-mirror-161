## -*- coding: utf-8; -*-

<script type="text/x-template" id="grid-filter-date-value-template">
  <div class="level">
    <div class="level-left">
      <div class="level-item">
        <tailbone-datepicker v-model="startDate"
                             ref="startDate"
                             @input="startDateChanged">
        </tailbone-datepicker>
      </div>
      <div v-show="dateRange"
           class="level-item">
        and
      </div>
      <div v-show="dateRange"
           class="level-item">
        <tailbone-datepicker v-model="endDate"
                             ref="endDate"
                             @input="endDateChanged">
        </tailbone-datepicker>
      </div>
    </div>
  </div>
</script>

<script type="text/x-template" id="grid-filter-template">

  <div class="level filter" v-show="filter.visible">
    <div class="level-left"
         style="align-items: start;">

      <div class="level-item filter-fieldname">

        <b-field>
          <b-checkbox-button v-model="filter.active" native-value="IGNORED">
            <b-icon pack="fas" icon="check" v-show="filter.active"></b-icon>
            <span>{{ filter.label }}</span>
          </b-checkbox-button>
        </b-field>

      </div>

      <b-field grouped v-show="filter.active"
               class="level-item"
               style="align-items: start;">

        <b-select v-model="filter.verb"
                  @input="focusValue()"
                  class="filter-verb">
          <option v-for="verb in filter.verbs"
                  :key="verb"
                  :value="verb">
            {{ filter.verb_labels[verb] }}
          </option>
        </b-select>

        ## only one of the following "value input" elements will be rendered

        <grid-filter-date-value v-if="filter.data_type == 'date'"
                                v-model="filter.value"
                                v-show="valuedVerb()"
                                :date-range="filter.verb == 'between'"
                                ref="valueInput">
        </grid-filter-date-value>

        <b-select v-if="filter.data_type == 'choice'"
                  v-model="filter.value"
                  v-show="valuedVerb()"
                  ref="valueInput">
          <option v-for="choice in filter.choices"
                  :key="choice"
                  :value="choice">
            {{ filter.choice_labels[choice] || choice }}
          </option>
        </b-select>

        <b-input v-if="filter.data_type == 'string' && !multiValuedVerb()"
                 v-model="filter.value"
                 v-show="valuedVerb()"
                 ref="valueInput">
        </b-input>

        <b-input v-if="filter.data_type == 'string' && multiValuedVerb()"
                 type="textarea"
                 v-model="filter.value"
                 v-show="valuedVerb()"
                 ref="valueInput">
        </b-input>

      </b-field>

    </div><!-- level-left -->
  </div><!-- level -->

</script>

<script type="text/x-template" id="${grid.component}-template">
  <div>

    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5em;">

      <div style="display: flex; flex-direction: column; justify-content: space-between;">
        <div></div>
        <div class="filters">
          % if grid.filterable:
              ## TODO: stop using |n filter
              ${grid.render_filters(template='/grids/filters_buefy.mako', allow_save_defaults=allow_save_defaults)|n}
          % endif
        </div>
      </div>

      <div style="display: flex; flex-direction: column; justify-content: space-between;">

        <div class="context-menu">
          % if context_menu:
              <ul id="context-menu">
                ## TODO: stop using |n filter
                ${context_menu|n}
              </ul>
          % endif
        </div>

        <div class="grid-tools-wrapper">
          % if tools:
              <div class="grid-tools field buttons is-grouped is-pulled-right">
                ## TODO: stop using |n filter
                ${tools|n}
              </div>
          % endif
        </div>

      </div>

    </div>

    <b-table
       :data="data"
       ## :columns="columns"
       :loading="loading"
       :row-class="getRowClass"

       ## TODO: this should be more configurable, maybe auto-detect based
       ## on buefy version??  probably cannot do that, but this feature
       ## is only supported with buefy 0.8.13 and newer
       % if request.rattail_config.getbool('tailbone', 'sticky_headers'):
       sticky-header
       height="600px"
       % endif

       :checkable="checkable"
       % if grid.checkboxes:
       :checked-rows.sync="checkedRows"
       % if grid.clicking_row_checks_box:
       @click="rowClick"
       % endif
       % endif
       % if grid.check_handler:
       @check="${grid.check_handler}"
       % endif
       % if grid.check_all_handler:
       @check-all="${grid.check_all_handler}"
       % endif
       ## TODO: definitely will be wanting this...
       ## :is-row-checkable=""

       :default-sort="[sortField, sortOrder]"
       backend-sorting
       @sort="onSort"

       :paginated="paginated"
       :per-page="perPage"
       :current-page="currentPage"
       backend-pagination
       :total="total"
       @page-change="onPageChange"

       ## TODO: should let grid (or master view) decide how to set these?
       icon-pack="fas"
       ## note that :striped="true" was interfering with row status (e.g. warning) styles
       :striped="false"
       :hoverable="true"
       :narrowed="true">

      <template slot-scope="props">
        % for column in grid_columns:
            <b-table-column field="${column['field']}"
                            label="${column['label']}"
                            :sortable="${json.dumps(column['sortable'])}"
                            % if grid.is_searchable(column['field']):
                            searchable
                            % endif
                            :visible="${json.dumps(column['visible'])}">
              % if grid.is_linked(column['field']):
                  <a :href="props.row._action_url_view" v-html="props.row.${column['field']}"></a>
              % else:
                  <span v-html="props.row.${column['field']}"></span>
              % endif
            </b-table-column>
        % endfor

        % if grid.main_actions or grid.more_actions:
            <b-table-column field="actions" label="Actions">
              ## TODO: we do not currently differentiate for "main vs. more"
              ## here, but ideally we would tuck "more" away in a drawer etc.
              % for action in grid.main_actions + grid.more_actions:
                  <a v-if="props.row._action_url_${action.key}"
                     :href="props.row._action_url_${action.key}"
                     class="grid-action${' has-text-danger' if action.key == 'delete' else ''} ${action.link_class or ''}"
                     % if action.click_handler:
                     @click.prevent="${action.click_handler}"
                     % endif
                     >
                    <i class="fas fa-${action.icon}"></i>
                    ${action.render_label()|n}
                  </a>
                  &nbsp;
              % endfor
            </b-table-column>
        % endif
      </template>

      <template #empty>
        <section class="section">
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
        </section>
      </template>

      % if grid.pageable:
      <template slot="footer">
        <b-field grouped position="is-right"
                 v-if="firstItem">
          <span class="control">
            showing {{ firstItem.toLocaleString('en') }} - {{ lastItem.toLocaleString('en') }} of {{ total.toLocaleString('en') }} results;
          </span>
          <b-select v-model="perPage"
                    size="is-small"
                    @input="loadAsyncData()">
            % for value in grid.get_pagesize_options():
                <option value="${value}">${value}</option>
            % endfor
          </b-select>
          <span class="control">
            per page
          </span>
        </b-field>
      </template>
      % endif

    </b-table>
  </div>
</script>

<script type="text/javascript">

  let ${grid.component_studly}CurrentData = ${json.dumps(grid_data['data'])|n}

  let ${grid.component_studly}Data = {
      loading: false,
      selectedFilter: null,
      ajaxDataUrl: ${json.dumps(grid.ajax_data_url)|n},

      data: ${grid.component_studly}CurrentData,
      rowStatusMap: ${json.dumps(grid_data['row_status_map'])|n},

      checkable: ${json.dumps(grid.checkboxes)|n},
      % if grid.checkboxes:
      checkedRows: ${grid_data['checked_rows_code']|n},
      % endif

      paginated: ${json.dumps(grid.pageable)|n},
      total: ${len(grid_data['data']) if static_data else grid_data['total_items']},
      perPage: ${json.dumps(grid.pagesize if grid.pageable else None)|n},
      currentPage: ${json.dumps(grid.page if grid.pageable else None)|n},
      firstItem: ${json.dumps(grid_data['first_item'] if grid.pageable else None)|n},
      lastItem: ${json.dumps(grid_data['last_item'] if grid.pageable else None)|n},

      sortField: ${json.dumps(grid.sortkey if grid.sortable else None)|n},
      sortOrder: ${json.dumps(grid.sortdir if grid.sortable else None)|n},

      ## filterable: ${json.dumps(grid.filterable)|n},
      filters: ${json.dumps(filters_data if grid.filterable else None)|n},
      filtersSequence: ${json.dumps(filters_sequence if grid.filterable else None)|n},
      selectedFilter: null,
  }

  let ${grid.component_studly} = {
      template: '#${grid.component}-template',

      props: {
          csrftoken: String,
      },

      computed: {
          // note, can use this with v-model for hidden 'uuids' fields
          selected_uuids: function() {
              return this.checkedRowUUIDs().join(',')
          },
      },

      methods: {

          getRowClass(row, index) {
              return this.rowStatusMap[index]
          },

          loadAsyncData(params, callback) {

              if (params === undefined || params === null) {
                  params = [
                      'partial=true',
                      `sortkey=${'$'}{this.sortField}`,
                      `sortdir=${'$'}{this.sortOrder}`,
                      `pagesize=${'$'}{this.perPage}`,
                      `page=${'$'}{this.currentPage}`
                  ].join('&')
              }

              this.loading = true
              this.$http.get(`${'$'}{this.ajaxDataUrl}?${'$'}{params}`).then(({ data }) => {
                  ${grid.component_studly}CurrentData = data.data
                  this.data = ${grid.component_studly}CurrentData
                  this.rowStatusMap = data.row_status_map
                  this.total = data.total_items
                  this.firstItem = data.first_item
                  this.lastItem = data.last_item
                  this.loading = false
                  this.checkedRows = this.locateCheckedRows(data.checked_rows)
                  if (callback) {
                      callback()
                  }
              })
              .catch((error) => {
                  this.data = []
                  this.total = 0
                  this.loading = false
                  throw error
              })
          },

          locateCheckedRows(checked) {
              let rows = []
              if (checked) {
                  for (let i = 0; i < this.data.length; i++) {
                      if (checked.includes(i)) {
                          rows.push(this.data[i])
                      }
                  }
              }
              return rows
          },

          onPageChange(page) {
              this.currentPage = page
              this.loadAsyncData()
          },

          onSort(field, order) {
              this.sortField = field
              this.sortOrder = order
              // always reset to first page when changing sort options
              // TODO: i mean..right? would we ever not want that?
              this.currentPage = 1
              this.loadAsyncData()
          },

          resetView() {
              this.loading = true
              location.href = '?reset-to-default-filters=true'
          },

          addFilter(filter_key) {

              // reset dropdown so user again sees "Add Filter" placeholder
              this.$nextTick(function() {
                  this.selectedFilter = null
              })

              // show corresponding grid filter
              this.filters[filter_key].visible = true
              this.filters[filter_key].active = true

              // track down the component
              var gridFilter = null
              for (var gf of this.$refs.gridFilters) {
                  if (gf.filter.key == filter_key) {
                      gridFilter = gf
                      break
                  }
              }

              // tell component to focus the value field, ASAP
              this.$nextTick(function() {
                  gridFilter.focusValue()
              })

          },

          applyFilters(params) {
              if (params === undefined) {
                  params = []
              }

              params.push('partial=true')
              params.push('filter=true')

              for (var key in this.filters) {
                  var filter = this.filters[key]
                  if (filter.active) {
                      params.push(key + '=' + encodeURIComponent(filter.value))
                      params.push(key + '.verb=' + encodeURIComponent(filter.verb))
                  } else {
                      filter.visible = false
                  }
              }

              this.loadAsyncData(params.join('&'))
          },

          clearFilters() {

              // explicitly deactivate all filters
              for (var key in this.filters) {
                  this.filters[key].active = false
              }

              // then just "apply" as normal
              this.applyFilters()
          },

          // explicitly set filters for the grid, to the given set.
          // this totally overrides whatever might be current.  the
          // new filter set should look like:
          //
          //     [
          //         {key: 'status_code',
          //          verb: 'equal',
          //          value: 1},
          //         {key: 'description',
          //          verb: 'contains',
          //          value: 'whatever'},
          //     ]
          //
          setFilters(newFilters) {
              for (let key in this.filters) {
                  let filter = this.filters[key]
                  let active = false
                  for (let newFilter of newFilters) {
                      if (newFilter.key == key) {
                          active = true
                          filter.active = true
                          filter.visible = true
                          filter.verb = newFilter.verb
                          filter.value = newFilter.value
                          break
                      }
                  }
                  if (!active) {
                      filter.active = false
                      filter.visible = false
                  }
              }
              this.applyFilters()
          },

          saveDefaults() {

              // apply current filters as normal, but add special directive
              const params = ['save-current-filters-as-defaults=true']
              this.applyFilters(params)
          },

          deleteObject(event) {
              // we let parent component/app deal with this, in whatever way makes sense...
              // TODO: should we ever provide anything besides the URL for this?
              this.$emit('deleteActionClicked', event.target.href)
          },

          checkedRowUUIDs() {
              let uuids = []
              for (let row of this.$data.checkedRows) {
                  uuids.push(row.uuid)
              }
              return uuids
          },

          allRowUUIDs() {
              let uuids = []
              for (let row of this.data) {
                  uuids.push(row.uuid)
              }
              return uuids
          },

          // when a user clicks a row, handle as if they clicked checkbox.
          // note that this method is only used if table is "checkable"
          rowClick(row) {
              let i = this.checkedRows.indexOf(row)
              if (i >= 0) {
                  this.checkedRows.splice(i, 1)
              } else {
                  this.checkedRows.push(row)
              }
              % if grid.check_handler:
              this.${grid.check_handler}(this.checkedRows, row)
              % endif
          },
      }
  }

</script>
