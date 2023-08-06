## -*- coding: utf-8 -*-
<%def name="grid_index_nav()">
  <div class="grid-nav">
    % if grid_index > 1:
        ${h.link_to(u"« Previous", '{}?index={}'.format(url('{}.view_index'.format(route_prefix)), grid_index - 1), class_='button')}
    % else:
        ${h.link_to(u"« Previous", '#', class_='button', disabled='disabled')}
    % endif
    <span class="viewing">viewing #${'{:,}'.format(grid_index)} of ${'{:,}'.format(grid_count)} results</span>
    % if grid_index < grid_count:
        ${h.link_to(u"Next »", '{}?index={}'.format(url('{}.view_index'.format(route_prefix)), grid_index + 1), class_='button')}
    % else:
        ${h.link_to(u"Next »", '#', class_='button', disabled='disabled')}
    % endif
  </div><!-- grid-nav -->
</%def>
