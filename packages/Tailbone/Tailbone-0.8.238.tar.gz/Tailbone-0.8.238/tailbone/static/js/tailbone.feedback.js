
$(function() {

    $('#feedback').click(function() {
        var dialog = $('#feedback-dialog');
        var form = dialog.find('form');
        var textarea = form.find('textarea');
        dialog.find('.referrer .field').html(location.href);
        textarea.val('');
        dialog.dialog({
            title: "User Feedback",
            width: 600,
            modal: true,
            buttons: [
                {
                    text: "Send",
                    click: function(event) {

                        var msg = $.trim(textarea.val());
                        if (! msg) {
                            alert("Please enter a message.");
                            textarea.select();
                            textarea.focus();
                            return;
                        }

                        disable_button(dialog_button(event));

                        var data = {
                            _csrf: form.find('input[name="_csrf"]').val(),
                            referrer: location.href,
                            user: form.find('input[name="user"]').val(),
                            user_name: form.find('input[name="user_name"]').val(),
                            message: msg
                        };

                        $.ajax(form.attr('action'), {
                            method: 'POST',
                            data: data,
                            success: function(data) {
                                dialog.dialog('close');
                                alert("Message successfully sent.\n\nThank you for your feedback.");
                            }
                        });

                    }
                },
                {
                    text: "Cancel",
                    click: function() {
                        dialog.dialog('close');
                    }
                }
            ]
        });
    });
    
});
