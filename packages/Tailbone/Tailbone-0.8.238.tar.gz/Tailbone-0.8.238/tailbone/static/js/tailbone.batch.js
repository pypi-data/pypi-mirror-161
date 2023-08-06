
/************************************************************
 *
 * tailbone.batch.js
 *
 * Common logic for view/edit batch pages
 *
 ************************************************************/


$(function() {
    
    $('#execute-batch').click(function() {
        if (has_execution_options) {
            $('#execution-options-dialog').dialog({
                title: "Execution Options",
                width: 600,
                modal: true,
                buttons: [
                    {
                        text: "Execute",
                        click: function(event) {
                            dialog_button(event).button('option', 'label', "Executing, please wait...").button('disable');
                            $('form[name="batch-execution"]').submit();
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
        } else {
            $(this).button('option', 'label', "Executing, please wait...").button('disable');
            $('form[name="batch-execution"]').submit();
        }
    });

});
