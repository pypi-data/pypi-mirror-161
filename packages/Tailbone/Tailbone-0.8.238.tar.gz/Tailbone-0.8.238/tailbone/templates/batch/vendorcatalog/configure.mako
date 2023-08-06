## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">
  ${self.input_file_templates_section()}

  <h3 class="block is-size-3">Options</h3>
  <div class="block" style="padding-left: 2rem;">

    <b-field>
      <b-checkbox name="rattail.batch.vendor_catalog.allow_future"
                  v-model="simpleSettings['rattail.batch.vendor_catalog.allow_future']"
                  native-value="true"
                  @input="settingsNeedSaved = true">
        Allow "future" cost changes
      </b-checkbox>
    </b-field>

  </div>

  <h3 class="block is-size-3">Catalog Parsers</h3>
  <div class="block" style="padding-left: 2rem;">

    <p class="block">
      Only the selected parsers will be exposed to users.
    </p>

    % for Parser in catalog_parsers:
        <b-field message="${Parser.key}">
          <b-checkbox name="catalog_parser_${Parser.key}"
                      v-model="catalogParsers['${Parser.key}']"
                      native-value="true"
                      @input="settingsNeedSaved = true">
            ${Parser.display}
          </b-checkbox>
        </b-field>
    % endfor

  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.catalogParsers = ${json.dumps(catalog_parsers_data)|n}

  </script>
</%def>


${parent.body()}
