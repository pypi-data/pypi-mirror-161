## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />
<%namespace file="/util.mako" import="view_profiles_helper" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if master.people_detachable and request.has_perm('{}.detach_person'.format(permission_prefix)):
      <script type="text/javascript">

        $(function() {
            $('.people .grid .actions a.detach').click(function() {
                if (! confirm("Are you sure you wish to detach this Person from the Customer?")) {
                    return false;
                }
            });
        });

      </script>
  % endif
</%def>

<%def name="object_helpers()">
  ${parent.object_helpers()}
  % if show_profiles_helper and instance.people:
      ${view_profiles_helper(instance.people)}
  % endif
</%def>

<%def name="render_buefy_form()">
  <div class="form">
    <tailbone-form @detach-person="detachPerson">
    </tailbone-form>
  </div>
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ${form.component_studly}Data.peopleData = ${json.dumps(people_data)|n}

    ThisPage.methods.detachPerson = function(url) {
        ## TODO: this should require POST, but we will add that once
        ## we can assume a Buefy theme is present, to avoid having to
        ## implement the logic in old jquery...
        if (confirm("Are you sure you want to detach this person from this customer account?")) {
            location.href = url
        }
    }

  </script>
</%def>

${parent.body()}
