## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if master.has_perm('runjob'):
      <nav class="panel">
        <p class="panel-heading">Tools</p>
        <div class="panel-block buttons">
          <once-button type="is-primary"
                       tag="a" href="${url('{}.runjob'.format(route_prefix), key=handler.get_key())}"
                       icon-pack="fas"
                       icon-left="arrow-circle-right"
                       text="Run ${handler.direction.capitalize()} Job">
          </once-button>
        </div>
      </nav>  
  % endif
</%def>


${parent.body()}
