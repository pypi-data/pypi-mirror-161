## -*- coding: utf-8; -*-
<%inherit file="/master/create.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    var report_descriptions = ${json.dumps(report_descriptions)|n};

    function show_description(key) {
        var desc = report_descriptions[key];
        $('#report-description').text(desc);
    }

    $(function() {

        var report_type = $('select[name="report_type"]');

        report_type.change(function(event) {
            show_description(report_type.val());
        });

    });

  </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">

    % if use_form:
        % if use_buefy:
            #report-description {
              margin-left: 2em;
            }
        % else:
            #report-description {
              margin-top: 2em;
              margin-left: 2em;
            }
        % endif
    % else:
        .report-selection {
          margin-left: 10em;
          margin-top: 3em;
        }

        .report-selection h3 {
            margin-top: 2em;
        }
    % endif

  </style>
</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <p>Please select the type of report you wish to generate.</p>
    <br />
    <div style="display: flex;">
      <tailbone-form v-on:report-change="reportChanged"></tailbone-form>
      <div id="report-description">{{ reportDescription }}</div>
    </div>
  </div>
</%def>

<%def name="page_content()">
  % if use_form:
      % if use_buefy:
          ${parent.page_content()}
      % else:
      <div class="form-wrapper">
        <p>Please select the type of report you wish to generate.</p>

        <div style="display: flex;">
          ${form.render()|n}
          <div id="report-description"></div>
        </div>

      </div><!-- form-wrapper -->
      % endif
  % else:
      <div>
        <br />
        <p>Please select the type of report you wish to generate.</p>

        <div class="report-selection">
          % for key in sorted_reports:
              <% report = reports[key] %>
              <h3>${h.link_to(report.name, url('generate_specific_report', type_key=key))}</h3>
              <p>${report.__doc__}</p>
          % endfor
        </div>
      </div>
  % endif
</%def>

<%def name="finalize_this_page_vars()">
  ${parent.finalize_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.reportDescriptions = ${json.dumps(report_descriptions)|n}

    TailboneForm.methods.reportTypeChanged = function(reportType) {
        this.$emit('report-change', this.reportDescriptions[reportType])
    }

    ThisPageData.reportDescription = null

    ThisPage.methods.reportChanged = function(description) {
        this.reportDescription = description
    }

  </script>
</%def>


${parent.body()}
