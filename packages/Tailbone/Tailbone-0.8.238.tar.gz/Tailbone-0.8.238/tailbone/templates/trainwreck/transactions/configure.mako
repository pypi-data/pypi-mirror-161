## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="form_content()">

  <h3 class="block is-size-3">Hidden Databases</h3>
  <div class="block" style="padding-left: 2rem;">
    % for key, engine in six.iteritems(trainwreck_engines):
        <b-field>
          <b-checkbox name="hidedb_${key}"
                      v-model="hiddenDatabases['${key}']"
                      native-value="true"
                      @input="settingsNeedSaved = true">
            ${key}
          </b-checkbox>
        </b-field>
    % endfor
  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.hiddenDatabases = ${json.dumps(hidden_databases)|n}

  </script>
</%def>


${parent.body()}
