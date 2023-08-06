## -*- coding: utf-8; -*-

<div class="form">
  ${form.render_deform(readonly=True)|n}
  % if buttons:
      ${buttons|n}
  % endif
</div><!-- form -->
