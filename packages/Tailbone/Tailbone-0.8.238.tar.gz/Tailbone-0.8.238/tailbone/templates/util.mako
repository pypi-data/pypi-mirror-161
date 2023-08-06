## -*- coding: utf-8; -*-

<%def name="view_profile_button(person)">
  <div class="buttons">
    % if use_buefy:
        <b-button type="is-primary"
                  tag="a" href="${url('people.view_profile', uuid=person.uuid)}"
                  icon-pack="fas"
                  icon-left="user">
          ${person}
        </b-button>
    % else:
        ${h.link_to(person, url('people.view_profile', uuid=person.uuid), class_='button is-primary')}
    % endif
  </div>
</%def>

<%def name="view_profiles_helper(people)">
  % if request.has_perm('people.view_profile'):
      % if use_buefy:
          <nav class="panel">
            <p class="panel-heading">Profiles</p>
            <div class="panel-block">
              <div style="display: flex; flex-direction: column;">
                <p class="block">View full profile for:</p>
                % for person in people:
                    ${view_profile_button(person)}
                % endfor
              </div>
            </div>
          </nav>
      % else:
          <div class="object-helper">
            <h3>Profiles</h3>
            <div class="object-helper-content">
              <p>View full profile for:</p>
              % for person in people:
                  ${view_profile_button(person)}
              % endfor
            </div>
          </div>
      % endif
  % endif
</%def>
