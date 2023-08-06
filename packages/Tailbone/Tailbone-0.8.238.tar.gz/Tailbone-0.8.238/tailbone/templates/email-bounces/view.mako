## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

## TODO: this page still uses jQuery but should use Vue.js

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    function autosize_message(scrolldown) {
        var msg = $('#message');
        var height = $(window).height() - msg.offset().top - 50;
        msg.height(height);
        if (scrolldown) {
            msg.animate({scrollTop: msg.get(0).scrollHeight - height}, 250);
        }
    }

    $(function () {
        autosize_message(true);
        $('#message').focus();
    });

    $(window).resize(function() {
        autosize_message(false);
    });

  </script>
  % endif
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  % if use_buefy:
  <style type="text/css">
    .email-message-body {
        border: 1px solid #000000;
        margin-top: 2rem;
        height: 500px;
    }
  </style>
  % else:
  <style type="text/css">
    #message {
        border: 1px solid #000000;
        height: 400px;
        overflow: auto;
        padding: 4px;
    }
  </style>
  % endif
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if use_buefy:
      <nav class="panel">
        <p class="panel-heading">Processing</p>
        <div class="panel-block">
          <div class="display: flex; flex-align: column;">
            % if bounce.processed:
                <p class="block">
                  This bounce was processed
                  ${h.pretty_datetime(request.rattail_config, bounce.processed)}
                  by ${bounce.processed_by}
                </p>
                % if master.has_perm('unprocess'):
                    <once-button type="is-warning"
                                 tag="a" href="${url('emailbounces.unprocess', uuid=bounce.uuid)}"
                                 text="Mark this bounce as UN-processed">
                    </once-button>
                % endif
            % else:
                <p class="block">
                  This bounce has NOT yet been processed.
                </p>
                % if master.has_perm('process'):
                    <once-button type="is-primary"
                                 tag="a" href="${url('emailbounces.process', uuid=bounce.uuid)}"
                                 text="Mark this bounce as Processed">
                    </once-button>
                % endif
            % endif
          </div>
        </div>
      </nav>
  % endif
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if not use_buefy:
  % if not bounce.processed and request.has_perm('emailbounces.process'):
      <li>${h.link_to("Mark this Email Bounce as Processed", url('emailbounces.process', uuid=bounce.uuid))}</li>
  % elif bounce.processed and request.has_perm('emailbounces.unprocess'):
      <li>${h.link_to("Mark this Email Bounce as UN-processed", url('emailbounces.unprocess', uuid=bounce.uuid))}</li>
  % endif
  % endif
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  % if not use_buefy:
  <pre id="message">
    ${message}
  </pre>
  % endif
</%def>

<%def name="render_this_page()">
  ${parent.render_this_page()}
  % if use_buefy:
      <pre class="email-message-body">
        ${message}
      </pre>
  % endif
</%def>

${parent.body()}
