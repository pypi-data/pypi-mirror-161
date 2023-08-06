## -*- coding: utf-8; -*-

<%def name="main_menu_items()">

  % for topitem in menus:
      <li>
        % if topitem['is_link']:
            ${h.link_to(topitem['title'], topitem['url'], target=topitem['target'])}
        % else:
            <a>${topitem['title']}</a>
            <ul>
              % for subitem in topitem['items']:
                  % if subitem['is_sep']:
                      <li>-</li>
                  % else:
                      <li>${h.link_to(subitem['title'], subitem['url'], target=subitem['target'])}</li>
                  % endif
              % endfor
            </ul>
        % endif
      </li>
  % endfor

  ## User Menu
  % if request.user:
      <li>
        % if messaging_enabled:
            <a${' class="root-user"' if request.is_root else ''|n}>${request.user}${" ({})".format(inbox_count) if inbox_count else ''}</a>
        % else:
            <a${' class="root-user"' if request.is_root else ''|n}>${request.user}</a>
        % endif
        <ul>
          % if request.is_root:
              <li class="root-user">${h.link_to("Stop being root", url('stop_root'))}</li>
          % elif request.is_admin:
              <li class="root-user">${h.link_to("Become root", url('become_root'))}</li>
          % endif
          % if messaging_enabled:
              <li>${h.link_to("Messages{}".format(" ({})".format(inbox_count) if inbox_count else ''), url('messages.inbox'))}</li>
          % endif
          <li>${h.link_to("Change Password", url('change_password'))}</li>
          <li>${h.link_to("Logout", url('logout'))}</li>
        </ul>
      </li>
  % else:
      <li>${h.link_to("Login", url('login'))}</li>
  % endif

</%def>
