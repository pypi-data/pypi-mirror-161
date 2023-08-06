## -*- coding: utf-8; -*-
<b-table
   :data="${data_prop}"
   icon-pack="fas"
   striped
   hoverable
   narrowed
   % if paginated:
   paginated
   per-page="${per_page}"
   % endif
   % if vshow is not Undefined and vshow:
   v-show="${vshow}"
   % endif
   % if loading is not Undefined and loading:
   :loading="${loading}"
   % endif
   % if grid.default_sortkey:
   :default-sort="['${grid.default_sortkey}', '${grid.default_sortdir}']"
   % endif
   >

  <template slot-scope="props">
    % for i, column in enumerate(grid_columns):
        <b-table-column field="${column['field']}"
                        % if not empty_labels:
                        label="${column['label']}"
                        % elif i > 0:
                        label=" "
                        % endif
                        ${'sortable' if column['sortable'] else ''}>
          % if empty_labels and i == 0:
              <template slot="header" slot-scope="{ column }"></template>
          % endif
          % if grid.is_linked(column['field']):
              <a :href="props.row._action_url_view"
                 v-html="props.row.${column['field']}"
                 % if view_click_handler:
                 @click.prevent="${view_click_handler}"
                 % endif
                 >
              </a>
          % elif grid.has_click_handler(column['field']):
              <span>
                <a href="#"
                   @click.prevent="${grid.click_handlers[column['field']]}"
                   v-html="props.row.${column['field']}">
                </a>
              </span>
          % else:
              <span v-html="props.row.${column['field']}"></span>
          % endif
        </b-table-column>
    % endfor

    % if grid.main_actions or grid.more_actions:
        <b-table-column field="actions" label="Actions">
          % for action in grid.main_actions:
              <a :href="props.row._action_url_${action.key}"
                 % if action.link_class:
                 class="${action.link_class}"
                 % else:
                 class="grid-action${' has-text-danger' if action.key == 'delete' else ''}"
                 % endif
                 % if action.click_handler:
                 @click.prevent="${action.click_handler}"
                 % endif
                 >
                <i class="fas fa-${action.icon}"></i>
                ${action.label}
              </a>
              &nbsp;
          % endfor
        </b-table-column>
    % endif
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

  % if show_footer is not Undefined and show_footer:
  <template slot="footer">
    <b-field grouped position="is-right">
      <span class="control">
        {{ ${data_prop}.length.toLocaleString('en') }} records
      </span>
    </b-field>
  </template>
  % endif

</b-table>
