
$(function() {

    $('input[name="username"]').keydown(function(event) {
        if (event.which == 13) {
            $('input[name="password"]').focus().select();
            return false;
        }
        return true;
    });

    $('form').submit(function() {
        if (! $('input[name="username"]').val()) {
            with ($('input[name="username"]').get(0)) {
                select();
                focus();
            }
            return false;
        }
        if (! $('input[name="password"]').val()) {
            with ($('input[name="password"]').get(0)) {
                select();
                focus();
            }
            return false;
        }
        return true;
    });

    $('input[name="username"]').focus();

});
