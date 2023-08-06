## -*- coding: utf-8; -*-
<%inherit file="/form.mako" />

<%def name="context_menu_item_delete()">
  % if not use_buefy and master.deletable and instance_deletable and master.has_perm('delete'):
      % if master.delete_confirm == 'simple':
          <li>
            ## note, the `ref` here is for buefy only
            ${h.form(action_url('delete', instance), ref='deleteObjectForm')}
            ${h.csrf_token(request)}
            <a href="${action_url('delete', instance)}"
               % if use_buefy:
               @click.prevent="deleteObject"
               % else:
               class="delete-instance"
               % endif
               >
              Delete this ${model_title}
            </a>
            ${h.end_form()}
          </li>
      % else:
          ## assuming here that: delete_confirm == 'full'
          <li>${h.link_to("Delete this {}".format(model_title), action_url('delete', instance))}</li>
      % endif
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if master.deletable and instance_deletable and request.has_perm('{}.delete'.format(permission_prefix)) and master.delete_confirm == 'simple':
      <script type="text/javascript">

        ThisPage.methods.deleteObject = function() {
            if (confirm("Are you sure you wish to delete this ${model_title}?")) {
                this.$refs.deleteObjectForm.submit()
            }
        }

      </script>
  % endif
</%def>


${parent.body()}
