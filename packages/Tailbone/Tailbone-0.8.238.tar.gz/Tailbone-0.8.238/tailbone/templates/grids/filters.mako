## -*- coding: utf-8; -*-
<div class="newfilters">

  ${h.form(form.action_url, method='get')}
    ${h.hidden('reset-to-default-filters', value='false')}
    ${h.hidden('save-current-filters-as-defaults', value='false')}

    <fieldset>
      <legend>Filters</legend>
      % for filtr in form.iter_filters():
          <div class="filter" id="filter-${filtr.key}" data-key="${filtr.key}"${' style="display: none;"' if not filtr.active else ''|n}>
            ${h.checkbox('{}-active'.format(filtr.key), class_='active', id='filter-active-{}'.format(filtr.key), checked=filtr.active)}
            <label for="filter-active-${filtr.key}">${filtr.label}</label>
            <div class="inputs" style="display: inline-block;">
              ${form.filter_verb(filtr)}
              ${form.filter_value(filtr)}
            </div>
          </div>
      % endfor
    </fieldset>

    <div class="buttons">
      <button type="submit" id="apply-filters">Apply Filters</button>
      <select id="add-filter">
        <option value="">Add a Filter</option>
        % for filtr in form.iter_filters():
            <option value="${filtr.key}"${' disabled="disabled"' if filtr.active else ''|n}>${filtr.label}</option>
        % endfor
      </select>
      <button type="button" id="default-filters">Default View</button>
      <button type="button" id="clear-filters">No Filters</button>
      % if allow_save_defaults and request.user:
          <button type="button" id="save-defaults">Save Defaults</button>
      % endif
    </div>

  ${h.end_form()}
</div><!-- newfilters -->
