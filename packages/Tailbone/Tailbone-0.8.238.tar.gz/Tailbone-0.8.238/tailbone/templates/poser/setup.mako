## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Poser Setup</%def>

<%def name="page_content()">
  <br />

  % if not poser_dir_exists:

      <p class="block">
        Before you can use Poser features, ${app_title} must create the
        file structure for it.
      </p>

      <p class="block">
        A new folder will be created at this location:&nbsp; &nbsp;
        <span class="is-family-monospace has-text-weight-bold">
          ${poser_dir}
        </span>
      </p>

      <p class="block">
        Once set up, ${app_title} can generate code for certain features,
        in the Poser folder.&nbsp; You can then access these features from
        within ${app_title}.
      </p>

      <p class="block">
        You are free to edit most files in the Poser folder as well.&nbsp;
        When you do so ${app_title} should pick up on the changes with no
        need for app restart.
      </p>

      <p class="block">
        Proceed?
      </p>

      ${h.form(request.current_route_url(), **{'@submit': 'setupSubmitting = true'})}
      ${h.csrf_token(request)}
      <b-button type="is-primary"
                native-type="submit"
                :disabled="setupSubmitting">
        {{ setupSubmitting ? "Working, please wait..." : "Go for it!" }}
      </b-button>
      ${h.end_form()}

  % else:

      <h3 class="is-size-3 block">Root Folder</h3>

      <p class="block">
        Poser folder already exists at:&nbsp; &nbsp;
        <span class="is-family-monospace has-text-weight-bold">
          ${poser_dir}
        </span>
      </p>

      ${h.form(request.current_route_url(), class_='block', **{'@submit': 'setupSubmitting = true'})}
      ${h.csrf_token(request)}
      ${h.hidden('action', value='refresh')}
      <b-button type="is-primary"
                native-type="submit"
                :disabled="setupSubmitting"
                icon-pack="fas"
                icon-left="redo">
        {{ setupSubmitting ? "Working, please wait..." : "Refresh Folder" }}
      </b-button>
      ${h.end_form()}

      <h3 class="is-size-3 block">Modules</h3>

      <ul class="list" style="max-width: 80%;">
        <li class="list-item">
          <span class="is-family-monospace">poser</span>
          <span class="is-pulled-right">
            % if poser_imported['poser']:
                <span class="is-family-monospace">
                  ${poser_imported['poser'].__file__}
                </span>
            % else:
                <span class="has-background-warning">
                  ${poser_import_errors['poser']}
                </span>
            % endif
          </span>
        </li>
        <li class="list-item">
          <span class="is-family-monospace">poser.reports</span>
          <span class="is-pulled-right">
            % if poser_imported['reports']:
                <span class="is-family-monospace">
                  ${poser_imported['reports'].__file__}
                </span>
            % else:
                <span class="has-background-warning">
                  ${poser_import_errors['reports']}
                </span>
            % endif
          </span>
        </li>
        <li class="list-item">
          <span class="is-family-monospace">poser.web.views</span>
          <span class="is-pulled-right">
            % if poser_imported['views']:
                <span class="is-family-monospace">
                  ${poser_imported['views'].__file__}
                </span>
            % else:
                <span class="has-background-warning">
                  ${poser_import_errors['views']}
                </span>
            % endif
          </span>
        </li>
      </ul>

  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.setupSubmitting = false

  </script>
</%def>


${parent.body()}
