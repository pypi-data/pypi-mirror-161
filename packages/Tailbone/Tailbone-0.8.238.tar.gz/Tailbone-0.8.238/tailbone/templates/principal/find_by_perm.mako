## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Find ${model_title_plural} by Permission</%def>

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    <% gcount = len(permissions) %>
    var permissions_by_group = {
    % for g, (gkey, group) in enumerate(permissions, 1):
        <% pcount = len(group['perms']) %>
        '${gkey}': {
        % for p, (pkey, perm) in enumerate(group['perms'], 1):
            '${pkey}': "${perm['label']}"${',' if p < pcount else ''}
        % endfor
        }${',' if g < gcount else ''}
    % endfor
    };

    $(function() {

        $('#permission_group').selectmenu({
            change: function(event, ui) {
                var perms = $('#permission');
                perms.find('option:first').siblings('option').remove();
                $.each(permissions_by_group[ui.item.value], function(key, label) {
                    perms.append($('<option value="' + key + '">' + label + '</option>'));
                });
                perms.selectmenu('refresh');
            }
        });

        $('#permission').selectmenu();

        $('#find-by-perm-form').submit(function() {
            $('.grid').remove();
            $(this).find('#submit').button('disable').button('option', 'label', "Searching, please wait...");
        });

    });

  </script>
  % endif
</%def>

<%def name="page_content()">
  % if use_buefy:
      <find-principals :permission-groups="permissionGroups"
                       :sorted-groups="sortedGroups">
      </find-principals>
  % else:
      ## not buefy
      ${h.form(request.current_route_url(), id='find-by-perm-form')}
      ${h.csrf_token(request)}

      <div class="form">
        ${self.wtfield(form, 'permission_group')}
        ${self.wtfield(form, 'permission')}
        <div class="buttons">
          ${h.submit('submit', "Find {}".format(model_title_plural))}
        </div>
      </div>

      ${h.end_form()}

      % if principals is not None:
      <div class="grid half">
        <br />
        <h2>${model_title_plural} with that permission (${len(principals)} total):</h2>
        ${self.principal_table()}
      </div>
      % endif
  % endif
</%def>

<%def name="render_this_page_template()">
  ${parent.render_this_page_template()}
  <script type="text/x-template" id="find-principals-template">
    <div class="app-wrapper">

      ${h.form(request.current_route_url(), **{'@submit': 'submitForm'})}
      ${h.csrf_token(request)}

      <div class="field-wrapper">
        <label for="permission_group">${form['permission_group'].label}</label>
        <div class="field">
          <b-select name="permission_group"
                    id="permission_group"
                    v-model="selectedGroup"
                    @input="selectGroup">
            <option v-for="groupkey in sortedGroups"
                    :key="groupkey"
                    :value="groupkey">
              {{ permissionGroups[groupkey].label }}
            </option>
          </b-select>
        </div>
      </div>

      <div class="field-wrapper">
        <label for="permission">${form['permission'].label}</label>
        <div class="field">
          <b-select name="permission"
                    v-model="selectedPermission">
            <option v-for="perm in groupPermissions"
                    :key="perm.permkey"
                    :value="perm.permkey">
              {{ perm.label }}
            </option>
          </b-select>
        </div>
      </div>

      <div class="buttons">
        <b-button type="is-primary"
                  native-type="submit"
                  :disabled="formSubmitting">
          {{ formButtonText }}
        </b-button>
      </div>

      ${h.end_form()}

      % if principals is not None:
      <div class="grid half">
        <br />
        <h2>Found ${len(principals)} ${model_title_plural} with permission: ${selected_permission}</h2>
        ${self.principal_table()}
      </div>
      % endif

    </div><!-- app-wrapper -->
  </script>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.permissionGroups = ${json.dumps(buefy_perms)|n}
    ThisPageData.sortedGroups = ${json.dumps(buefy_sorted_groups)|n}

  </script>
</%def>

<%def name="make_this_page_component()">
  ${parent.make_this_page_component()}
  <script type="text/javascript">

    Vue.component('find-principals', {
        template: '#find-principals-template',
        props: {
            permissionGroups: Object,
            sortedGroups: Array
        },
        data() {
            return {
                groupPermissions: ${json.dumps(buefy_perms.get(selected_group, {}).get('permissions', []))|n},
                selectedGroup: ${json.dumps(selected_group)|n},
                % if selected_permission:
                selectedPermission: ${json.dumps(selected_permission)|n},
                % elif selected_group in buefy_perms:
                selectedPermission: ${json.dumps(buefy_perms[selected_group]['permissions'][0]['permkey'])|n},
                % else:
                selectedPermission: null,
                % endif
                formButtonText: "Find ${model_title_plural}",
                formSubmitting: false,
            }
        },
        methods: {

            selectGroup(groupkey) {

                // re-populate Permission dropdown, auto-select first option
                this.groupPermissions = this.permissionGroups[groupkey].permissions
                this.selectedPermission = this.groupPermissions[0].permkey
            },

            submitForm() {
                this.formSubmitting = true
                this.formButtonText = "Working, please wait..."
            }
        }
    })

  </script>
</%def>


${parent.body()}
