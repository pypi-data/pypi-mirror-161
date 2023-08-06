## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="extra_javascript()">
  ${parent.extra_javascript()}
  <script type="text/javascript">

    function update_change_status_button() {
        var count = $('.grid tr:not(.header) td.checkbox input:checked').length;
        $('button.change-status').button('option', 'disabled', count < 1);
    }

    $(function() {

        $('.grid-wrapper').on('click', 'tr.header td.checkbox input', function() {
            update_change_status_button();
        });

        $('.grid-wrapper').on('click', '.grid tr:not(.header) td.checkbox input', function() {
            update_change_status_button();
        });
        $('.grid-wrapper').on('click', '.grid tr:not(.header)', function() {
            update_change_status_button();
        });

        $('button.change-status').click(function() {
            var uuids = [];
            $('.grid tr:not(.header) td.checkbox input:checked').each(function() {
                uuids.push($(this).parents('tr:first').data('uuid'));
            });
            if (! uuids.length) {
                alert("You must first select one or more credits.");
                return false;
            }

            var form = $('form[name="change-status"]');
            form.find('[name="uuids"]').val(uuids.toString());

            $('#change-status-dialog').dialog({
                title: "Change Credit Status",
                width: 500,
                height: 300,
                modal: true,
                open: function() {
                    // TODO: why must we do this here instead of using auto-enhance ?
                    $('#change-status-dialog select[name="status"]').selectmenu();
                },
                buttons: [
                    {
                        text: "Submit",
                        click: function(event) {
                            disable_button(dialog_button(event));
                            form.submit();
                        }
                    },
                    {
                        text: "Cancel",
                        click: function() {
                            $(this).dialog('close');
                        }
                    }
                ]
            });
        });

    });
  </script>
</%def>

<%def name="grid_tools()">
  ${parent.grid_tools()}
  <button type="button" class="change-status" disabled="disabled">Change Status</button>
</%def>

${parent.body()}

<div id="change-status-dialog" style="display: none;">
  ${h.form(url('purchases.credits.change_status'), name='change-status')}
  ${h.csrf_token(request)}
  ${h.hidden('uuids')}

  <br />
  <p>Please choose the appropriate status for the selected credits.</p>

  <div class="fieldset">

  <div class="field-wrapper status">
    <label for="status">Status</label>
    <div class="field">
      ${h.select('status', None, status_options)}
    </div>
  </div>

  </div>

  ${h.end_form()}
</div>
