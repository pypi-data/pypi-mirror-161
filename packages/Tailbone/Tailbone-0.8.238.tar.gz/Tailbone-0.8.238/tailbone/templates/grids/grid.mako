## -*- coding: utf-8; -*-
<div class="grid ${grid_class}" data-delete-speedbump="${'true' if grid.delete_speedbump else 'false'}" ${h.HTML.render_attrs(grid_attrs)}>
  <table>
    ${grid.make_webhelpers_grid()}
  </table>
  % if grid.pageable and grid.pager:
      <div class="pager">
        <p class="showing">
          ${"showing {} thru {} of {:,d}".format(grid.pager.first_item, grid.pager.last_item, grid.pager.item_count)}
          % if grid.pager.page_count > 1:
              ${"(page {} of {:,d})".format(grid.pager.page, grid.pager.page_count)}
          % endif
        </p>
        <p class="page-links">
          ${h.select('pagesize', grid.pager.items_per_page, grid.get_pagesize_options())}
          per page&nbsp;
          ${grid.pager.pager('$link_first $link_previous ~1~ $link_next $link_last', symbol_next='next', symbol_previous='prev')|n}
        </p>
      </div>
  % endif
</div>
