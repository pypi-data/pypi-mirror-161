
/************************************************************
 *
 * tailbone.appsettings.js
 *
 * Logic for App Settings page.
 *
 ************************************************************/


function show_group(group) {
    if (group == "(All)") {
        $('.panel').show();
    } else {
        $('.panel').hide();
        $('.panel[data-groupname="' + group + '"]').show();
    }
}


$(function() {

    $('#settings-group').on('selectmenuchange', function(event, ui) {
        show_group(ui.item.value);
    });

    show_group($('#settings-group').val());

});
