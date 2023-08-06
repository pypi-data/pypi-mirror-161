## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  <script type="text/javascript">

    ## NOTE: we must delay activation of accordions, otherwise they do not
    ## seem to "resize" correctly
    var customer_accordion_activated = false;
    var user_accordion_activated = false;

    $(function() {
        $('#profile-tabs').tabs({
            activate: function(event, ui) {
                ## activate accordion, first time tab is activated
                if (ui.newPanel.selector == '#customer-tab') {
                    if (! customer_accordion_activated) {
                        $('#customers-accordion').accordion();
                        customer_accordion_activated = true;
                    }
                } else if (ui.newPanel.selector == '#user-tab') {
                    if (! user_accordion_activated) {
                        $('#users-accordion').accordion();
                        user_accordion_activated = true;
                    }
                }
            }
        });
    });
  </script>
</%def>

<div id="profile-tabs">
  <ul>
    <li><a href="#personal-tab">Personal</a></li>
    <li><a href="#customer-tab">Customer</a></li>
    <li><a href="#employee-tab">Employee</a></li>
    <li><a href="#user-tab">User</a></li>
  </ul>

  <div id="personal-tab">

    <div style="display: flex; justify-content: space-between;">

      <div>

        <div class="field-wrapper first_name">
          <div class="field-row">
            <label>First Name</label>
            <div class="field">
              ${person.first_name}
            </div>
          </div>
        </div>

        <div class="field-wrapper middle_name">
          <div class="field-row">
            <label>Middle Name</label>
            <div class="field">
              ${person.middle_name}
            </div>
          </div>
        </div>

        <div class="field-wrapper last_name">
          <div class="field-row">
            <label>Last Name</label>
            <div class="field">
              ${person.last_name}
            </div>
          </div>
        </div>

        <div class="field-wrapper street">
          <div class="field-row">
            <label>Street 1</label>
            <div class="field">
              ${person.address.street if person.address else ''}
            </div>
          </div>
        </div>

        <div class="field-wrapper street2">
          <div class="field-row">
            <label>Street 2</label>
            <div class="field">
              ${person.address.street2 if person.address else ''}
            </div>
          </div>
        </div>

        <div class="field-wrapper city">
          <div class="field-row">
            <label>City</label>
            <div class="field">
              ${person.address.city if person.address else ''}
            </div>
          </div>
        </div>

        <div class="field-wrapper state">
          <div class="field-row">
            <label>State</label>
            <div class="field">
              ${person.address.state if person.address else ''}
            </div>
          </div>
        </div>

        <div class="field-wrapper zipcode">
          <div class="field-row">
            <label>Zipcode</label>
            <div class="field">
              ${person.address.zipcode if person.address else ''}
            </div>
          </div>
        </div>

        % if person.phones:
            % for phone in person.phones:
                <div class="field-wrapper">
                  <div class="field-row">
                    <label>Phone Number</label>
                    <div class="field">
                      ${phone.number} (type: ${phone.type})
                    </div>
                  </div>
                </div>
            % endfor
        % else:
            <div class="field-wrapper">
              <div class="field-row">
                <label>Phone Number</label>
                <div class="field">
                  (none on file)
                </div>
              </div>
            </div>
        % endif

        % if person.emails:
            % for email in person.emails:
                <div class="field-wrapper">
                  <div class="field-row">
                    <label>Email Address</label>
                    <div class="field">
                      ${email.address} (type: ${email.type})
                    </div>
                  </div>
                </div>
            % endfor
        % else:
            <div class="field-wrapper">
              <div class="field-row">
                <label>Email Address</label>
                <div class="field">
                  (none on file)
                </div>
              </div>
            </div>
        % endif

      </div>

      <div>
        % if request.has_perm('people.view'):
            ${h.link_to("View Person", url('people.view', uuid=person.uuid), class_='button')}
        % endif
      </div>

    </div>
  </div><!-- personal-tab -->

  <div id="customer-tab">
    % if person.customers:
        <p>${person} is associated with ${len(person.customers)} customer account(s)</p>
        <br />
        <div id="customers-accordion">
          % for customer in person.customers:
              <h3>${customer.id} - ${customer.name}</h3>
              <div>

                <div style="display: flex; justify-content: space-between;">

                  <div>

                    <div class="field-wrapper id">
                      <div class="field-row">
                        <label>ID</label>
                        <div class="field">
                          ${customer.id or ''}
                        </div>
                      </div>
                    </div>

                    <div class="field-wrapper name">
                      <div class="field-row">
                        <label>Name</label>
                        <div class="field">
                          ${customer.name}
                        </div>
                      </div>
                    </div>

                    % if customer.phones:
                        % for phone in customer.phones:
                            <div class="field-wrapper">
                              <div class="field-row">
                                <label>Phone Number</label>
                                <div class="field">
                                  ${phone.number} (type: ${phone.type})
                                </div>
                              </div>
                            </div>
                        % endfor
                    % else:
                        <div class="field-wrapper">
                          <div class="field-row">
                            <label>Phone Number</label>
                            <div class="field">
                              (none on file)
                            </div>
                          </div>
                        </div>
                    % endif

                    % if customer.emails:
                        % for email in customer.emails:
                            <div class="field-wrapper">
                              <div class="field-row">
                                <label>Email Address</label>
                                <div class="field">
                                  ${email.address} (type: ${email.type})
                                </div>
                              </div>
                            </div>
                        % endfor
                    % else:
                        <div class="field-wrapper">
                          <div class="field-row">
                            <label>Email Address</label>
                            <div class="field">
                              (none on file)
                            </div>
                          </div>
                        </div>
                    % endif

                  </div>

                  <div>
                    % if request.has_perm('customers.view'):
                        ${h.link_to("View Customer", url('customers.view', uuid=customer.uuid), class_='button')}
                    % endif
                  </div>

                </div>

              </div>
          % endfor
        </div>

    % else:
        <p>${person} has never been a customer.</p>
    % endif
  </div><!-- customer-tab -->

  <div id="employee-tab">
    % if employee:
        <div style="display: flex; justify-content: space-between;">

          <div>

            <div class="field-wrapper id">
              <div class="field-row">
                <label>ID</label>
                <div class="field">
                  ${employee.id or ''}
                </div>
              </div>
            </div>

            <div class="field-wrapper display_name">
              <div class="field-row">
                <label>Display Name</label>
                <div class="field">
                  ${employee.display_name or ''}
                </div>
              </div>
            </div>

            <div class="field-wrapper status">
              <div class="field-row">
                <label>Status</label>
                <div class="field">
                  ${enum.EMPLOYEE_STATUS.get(employee.status, '')}
                </div>
              </div>
            </div>

            % if employee.phones:
                % for phone in employee.phones:
                    <div class="field-wrapper">
                      <div class="field-row">
                        <label>Phone Number</label>
                        <div class="field">
                          ${phone.number} (type: ${phone.type})
                        </div>
                      </div>
                    </div>
                % endfor
            % else:
                <div class="field-wrapper">
                  <div class="field-row">
                    <label>Phone Number</label>
                    <div class="field">
                      (none on file)
                    </div>
                  </div>
                </div>
            % endif

            % if employee.emails:
                % for email in employee.emails:
                    <div class="field-wrapper">
                      <div class="field-row">
                        <label>Email Address</label>
                        <div class="field">
                          ${email.address} (type: ${email.type})
                        </div>
                      </div>
                    </div>
                % endfor
            % else:
                <div class="field-wrapper">
                  <div class="field-row">
                    <label>Email Address</label>
                    <div class="field">
                      (none on file)
                    </div>
                  </div>
                </div>
            % endif

          </div>

          <div>
            % if request.has_perm('employees.view'):
                ${h.link_to("View Employee", url('employees.view', uuid=employee.uuid), class_='button')}
            % endif
          </div>

        </div>

    % else:
        <p>${person} has never been an employee.</p>
    % endif
  </div><!-- employee-tab -->

  <div id="user-tab">
    % if person.users:
        <p>${person} is associated with ${len(person.users)} user account(s)</p>
        <br />
        <div id="users-accordion">
          % for user in person.users:
              <h3>${user.username}</h3>
              <div>

                <div style="display: flex; justify-content: space-between;">

                  <div>

                    <div class="field-wrapper id">
                      <div class="field-row">
                        <label>Username</label>
                        <div class="field">
                          ${user.username}
                        </div>
                      </div>
                    </div>

                  </div>

                  <div>
                    % if request.has_perm('users.view'):
                        ${h.link_to("View User", url('users.view', uuid=user.uuid), class_='button')}
                    % endif
                  </div>

                </div>

              </div>
          % endfor
        </div>

    % else:
        <p>${person} has never been a user.</p>
    % endif
  </div><!-- user-tab -->

</div><!-- profile-tabs -->
