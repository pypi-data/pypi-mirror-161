## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">
    $(function() {
        $('#restart-client').click(function() {
            disable_button(this);
            location.href = '${url('tempmon.clients.restart', uuid=instance.uuid)}';
        });
    });
  </script>
  % endif
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if request.has_perm('tempmon.appliances.dashboard'):
      <li>${h.link_to("Go to the Dashboard", url('tempmon.dashboard'))}</li>
  % endif
</%def>

<%def name="object_helpers()">
  % if instance.enabled and master.restartable_client(instance) and request.has_perm('{}.restart'.format(route_prefix)):
      <div class="object-helper">
        <h3>Client Tools</h3>
        <div class="object-helper-content">
          % if use_buefy:
              <once-button tag="a" href="${url('{}.restart'.format(route_prefix), uuid=instance.uuid)}"
                           type="is-primary"
                           text="Restart tempmon-client daemon">
              </once-button>
          % else:
          <button type="button" id="restart-client">Restart tempmon-client daemon</button>
          % endif
        </div>
      </div>
  % endif
</%def>

${parent.body()}
