## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  % if not use_buefy:
  <script type="text/javascript">

    function show_packages(type) {
        if (type == 'all') {
            $('.showing .diffs').css('font-weight', 'normal');
            $('table.diff tbody tr').show();
            $('.showing .all').css('font-weight', 'bold');
        } else if (type == 'diffs') {
            $('.showing .all').css('font-weight', 'normal');
            $('table.diff tbody tr:not(.diff)').hide();
            $('.showing .diffs').css('font-weight', 'bold');
        }
    }

    $(function() {

        show_packages('diffs');

        $('.showing .all').click(function() {
            show_packages('all');
            return false;
        });

        $('.showing .diffs').click(function() {
            show_packages('diffs')
            return false;
        });

    });

  </script>
  % endif
</%def>

<%def name="render_form_buttons()">
  % if not instance.executed and instance.status_code == enum.UPGRADE_STATUS_PENDING and request.has_perm('{}.execute'.format(permission_prefix)):
      <div class="buttons">
        % if instance.enabled and not instance.executing:
            % if use_buefy:
            ${h.form(url('{}.execute'.format(route_prefix), uuid=instance.uuid), **{'@submit': 'submitForm'})}
            % else:
            ${h.form(url('{}.execute'.format(route_prefix), uuid=instance.uuid), class_='autodisable')}
            % endif
            ${h.csrf_token(request)}
            % if use_buefy:
                <b-button type="is-primary"
                          native-type="submit"
                          :disabled="formSubmitting">
                  {{ formButtonText }}
                </b-button>
            % else:
                ${h.submit('execute', "Execute this upgrade", class_='button is-primary')}
            % endif
            ${h.end_form()}
        % elif instance.enabled:
            <button type="button" class="button is-primary" disabled="disabled" title="This upgrade is currently executing">Execute this upgrade</button>
        % else:
            <button type="button" class="button is-primary" disabled="disabled" title="This upgrade is not enabled">Execute this upgrade</button>
        % endif
      </div>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    TailboneFormData.showingPackages = 'diffs'

    TailboneFormData.formButtonText = "Execute this upgrade"
    TailboneFormData.formSubmitting = false

    TailboneForm.methods.submitForm = function() {
        this.formSubmitting = true
        this.formButtonText = "Working, please wait..."
    }

  </script>
</%def>


${parent.body()}
