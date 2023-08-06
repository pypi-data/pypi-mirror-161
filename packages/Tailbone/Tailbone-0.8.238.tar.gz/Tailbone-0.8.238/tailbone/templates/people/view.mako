## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy and not instance.users and request.has_perm('users.create'):
      <script type="text/javascript">
        ## TODO: should do this differently for Buefy themes
        $(function() {
            $('#make-user').click(function() {
                if (confirm("Really make a user account for this person?")) {
                    % if not use_buefy:
                    disable_button(this);
                    % endif
                    $('form[name="make-user-form"]').submit();
                }
            });
        });
      </script>
  % endif
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  ${view_profiles_helper([instance])}
</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <tailbone-form v-on:make-user="makeUser"></tailbone-form>
  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneForm.methods.clickMakeUser = function(event) {
        this.$emit('make-user')
    }

    ThisPage.methods.makeUser = function(event) {
        if (confirm("Really make a user account for this person?")) {
            this.$refs.makeUserForm.submit()
        }
    }

  </script>
</%def>

<%def name="page_content()">
  ${parent.page_content()}
  % if not instance.users and request.has_perm('users.create'):
      % if use_buefy:
          ${h.form(url('people.make_user'), ref='makeUserForm')}
      % else:
          ${h.form(url('people.make_user'), name='make-user-form')}
      % endif
      ${h.csrf_token(request)}
      ${h.hidden('person_uuid', value=instance.uuid)}
      ${h.end_form()}
  % endif
</%def>


${parent.body()}

