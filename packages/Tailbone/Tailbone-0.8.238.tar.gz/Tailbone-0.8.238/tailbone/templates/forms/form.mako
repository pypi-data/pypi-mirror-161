## -*- coding: utf-8; -*-
% if form.use_buefy:
    ${form.render_deform(buttons=buttons)|n}
% else:
    <div class="form">
      ${form.render_deform(buttons=buttons)|n}
    </div>
% endif
