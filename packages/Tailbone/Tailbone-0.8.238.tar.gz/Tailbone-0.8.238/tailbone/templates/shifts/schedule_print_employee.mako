## -*- coding: utf-8; -*-
<%namespace file="/shifts/base.mako" import="timesheet" />
<%namespace file="/shifts/schedule.mako" import="render_day" />
<html>
  <head>
    ## TODO: this seems a little hacky..?
    ${h.stylesheet_link(request.static_url('tailbone:static/css/normalize.css'), media='all')}
    ${h.stylesheet_link(request.static_url('tailbone:static/css/base.css'), media='all')}
    ${h.stylesheet_link(request.static_url('tailbone:static/css/grids.css'), media='all')}
    ${h.stylesheet_link(request.static_url('tailbone:static/css/timesheet.css'), media='all')}
    ${h.stylesheet_link(request.static_url('tailbone:static/css/schedule_print.css'), media='print')}
  </head>
  <body>
    <h1>
      ${employee} -
      ${week_of}
    </h1>
    ${timesheet(render_day=render_day)}
  </body>
</html>
