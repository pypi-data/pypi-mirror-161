## -*- coding: utf-8 -*-
<div class="filters" url="${search.request.current_route_url()}">
  ${search.begin()}
  ${search.hidden('filters', 'true')}
  <% visible = [] %>
  % for f in search.sorted_filters():
      <div class="filter" id="filter-${f.name}"${' style="display: none;"' if not search.config.get('include_filter_'+f.name) else ''|n}>
        ${search.checkbox('include_filter_'+f.name)}
        <label for="${f.name}">${f.label}</label>
        ${f.types_select()}
        <div class="value">
          ${f.value_control()}
        </div>
      </div>
      % if search.config.get('include_filter_'+f.name):
          <% visible.append(f.name) %>
      % endif
  % endfor
  <div class="buttons">
    ${search.add_filter(visible)}
    ${search.submit('submit', "Search", style='display: none;' if not visible else None)}
    <button type="reset"${' style="display: none;"' if not visible else ''|n}>Reset</button>
  </div>
  ${search.end()}
  % if visible:
      <script language="javascript" type="text/javascript">
        filters_to_disable = [
          % for field in visible:
              '${field}',
          % endfor
        ];
        $(function() {
            disable_filter_options();
        });
      </script>
  % endif
</div>
