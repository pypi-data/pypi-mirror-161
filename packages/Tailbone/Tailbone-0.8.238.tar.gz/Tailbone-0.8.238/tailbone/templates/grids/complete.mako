## -*- coding: utf-8 -*-
<div class="grid-wrapper">

  <table class="grid-header">
    <tbody>
      <tr>

        <td class="filters" rowspan="2">
          % if grid.filterable:
              ${grid.render_filters(allow_save_defaults=allow_save_defaults)|n}
          % endif
        </td>

        <td class="menu">
          % if context_menu:
              <ul id="context-menu">
                ${context_menu|n}
              </ul>
          % endif
        </td>
      </tr>

      <tr>
        <td class="tools">
          % if tools:
              <div class="grid-tools">
                ${tools|n}
              </div><!-- grid-tools -->
          % endif
        </td>
      </tr>

    </tbody>
  </table><!-- grid-header -->

  ${grid.render_grid()|n}

</div><!-- grid-wrapper -->
