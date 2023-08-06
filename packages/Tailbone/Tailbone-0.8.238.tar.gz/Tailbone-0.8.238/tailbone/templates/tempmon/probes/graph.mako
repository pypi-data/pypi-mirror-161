## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="title()">Temperature Graph</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.bundle.min.js"></script>
  % if not use_buefy:
  <script type="text/javascript">

    var ctx = null;
    var chart = null;

    function fetchReadings(timeRange) {
        if (timeRange === undefined) {
            timeRange = $('#time-range').val();
        }

        var timeUnit;
        if (timeRange == 'last hour') {
            timeUnit = 'minute';
        } else if (['last 6 hours', 'last day'].includes(timeRange)) {
            timeUnit = 'hour';
        } else {
            timeUnit = 'day';
        }

        $('.form-wrapper').mask("Fetching data");
        if (chart) {
            chart.destroy();
        }

        $.get('${url('{}.graph_readings'.format(route_prefix), uuid=probe.uuid)}', {'time-range': timeRange}, function(data) {

            chart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: "${probe.description}",
                        data: data
                    }]
                },
                options: {
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {unit: timeUnit},
                            position: 'bottom'
                        }]
                    }
                }
            });

            $('.form-wrapper').unmask();
        });
    }

    $(function() {

        ctx = $('#tempchart');

        $('#time-range').selectmenu({
            change: function(event, ui) {
                fetchReadings(ui.item.value);
            }
        });

        fetchReadings();
    });

  </script>
  % endif
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if master.has_perm('view'):
      <li>${h.link_to("View this {}".format(model_title), master.get_action_url('view', probe))}</li>
  % endif
  % if request.has_perm('tempmon.appliances.dashboard'):
      <li>${h.link_to("Go to the Dashboard", url('tempmon.dashboard'))}</li>
  % endif
</%def>

<%def name="render_this_page()">
  <div style="display: flex; justify-content: space-between;">

    <div class="form-wrapper">
      <div class="form">

        % if use_buefy:
            <b-field horizontal label="Appliance">
              <div>
                % if probe.appliance:
                    <a href="${url('tempmon.appliances.view', uuid=probe.appliance.uuid)}">${probe.appliance}</a>
                % endif
              </div>
            </b-field>
        % else:
            <div class="field-wrapper">
              <label>Appliance</label>
              <div class="field">
                % if probe.appliance:
                    <a href="${url('tempmon.appliances.view', uuid=probe.appliance.uuid)}">${probe.appliance}</a>
                % endif
              </div>
            </div>
        % endif

        % if use_buefy:
            <b-field horizontal label="Probe Location">
              <div>
                ${probe.location or ""}
              </div>
            </b-field>
        % else:
            <div class="field-wrapper">
              <label>Probe Location</label>
              <div class="field">${probe.location or ""}</div>
            </div>
        % endif

        % if use_buefy:
            <b-field horizontal label="Showing">
              ${time_range}
            </b-field>
        % else:
            <div class="field-wrapper">
              <label>Showing</label>
              <div class="field">
                ${time_range}
              </div>
            </div>
        % endif

      </div>
    </div>

    <div style="display: flex; align-items: flex-start;">
      <div class="object-helpers">
        ${self.object_helpers()}
      </div>

      <ul id="context-menu">
        ${self.context_menu_items()}
      </ul>
    </div>

  </div>

  % if use_buefy:
      <canvas ref="tempchart" width="400" height="150"></canvas>
  % else:
      <canvas id="tempchart" width="400" height="150"></canvas>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.currentTimeRange = ${json.dumps(current_time_range)|n}
    ThisPageData.chart = null

    ThisPage.methods.fetchReadings = function(timeRange) {

        if (timeRange === undefined) {
            timeRange = this.currentTimeRange
        }

        let timeUnit = null
        if (timeRange == 'last hour') {
            timeUnit = 'minute'
        } else if (['last 6 hours', 'last day'].includes(timeRange)) {
            timeUnit = 'hour'
        } else {
            timeUnit = 'day'
        }

        if (this.chart) {
            this.chart.destroy()
        }

        this.$http.get('${url('{}.graph_readings'.format(route_prefix), uuid=probe.uuid)}', {params: {'time-range': timeRange}}).then(({ data }) => {

            this.chart = new Chart(this.$refs.tempchart, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: "${probe.description}",
                        data: data
                    }]
                },
                options: {
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {unit: timeUnit},
                            position: 'bottom'
                        }]
                    }
                }
            });

        })
    }

    ThisPage.methods.timeRangeChanged = function(value) {
        this.fetchReadings(value)
    }

    ThisPage.mounted = function() {
        this.fetchReadings()
    }

  </script>
</%def>


${parent.body()}
