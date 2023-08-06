## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">${index_title} &raquo; Yearly Rollover</%def>

<%def name="content_title()">Yearly Rollover</%def>

<%def name="page_content()">
  <br />

  % if six.text_type(next_year) not in trainwreck_engines:
      <b-notification type="is-warning">
        You do not have a database configured for next year (${next_year}).&nbsp;
        You should be sure to configure it before next year rolls around.
      </b-notification>
  % endif

  <p class="block">
    The following Trainwreck databases are configured:
  </p>

  <b-table :data="engines">
    <template slot-scope="props">
      <b-table-column field="key" label="DB Key">
        {{ props.row.key }}
      </b-table-column>
      <b-table-column field="oldest_date" label="Oldest Date">
        <span v-if="props.row.error" class="has-text-danger">
          error
        </span>
        <span v-if="!props.row.error">
          {{ props.row.oldest_date }}
        </span>
      </b-table-column>
      <b-table-column field="newest_date" label="Newest Date">
        <span v-if="props.row.error" class="has-text-danger">
          error
        </span>
        <span v-if="!props.row.error">
          {{ props.row.newest_date }}
        </span>
      </b-table-column>
    </template>
  </b-table>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.engines = ${json.dumps(engines_data)|n}

  </script>
</%def>


${parent.body()}
