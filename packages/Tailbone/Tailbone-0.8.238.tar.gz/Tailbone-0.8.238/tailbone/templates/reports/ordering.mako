## -*- coding: utf-8 -*-
<%inherit file="/reports/base.mako" />

<%def name="title()">Report : Ordering Worksheet</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">

    div.grid {
        clear: none;
    }

  </style>
</%def>

<p>Please provide the following criteria to generate your report:</p>
<br />

${h.form(request.current_route_url())}
${h.hidden('departments', value='')}

<div class="field-wrapper">
  ${h.hidden('vendor', value='')}
  <label for="vendor-name">Vendor:</label>
  ${h.text('vendor-name', size='40', value='')}
  <div id="vendor-display" style="display: none;">
    <span>(no vendor)</span>&nbsp;
    <button type="button" id="change-vendor">Change</button>
  </div>
</div>

<div class="field-wrapper">
  <label>Departments:</label>
  <div class="grid"></div>
</div>

<div class="field-wrapper">
  ${h.checkbox('preferred_only', label="Include only those products for which this vendor is preferred.", checked=True)}
</div>

<div class="buttons">
  ${h.submit('submit', "Generate Report")}
</div>

${h.end_form()}

<script type="text/javascript">

$(function() {

    var autocompleter = $('#vendor-name').autocomplete({
        serviceUrl: '${url('vendors.autocomplete')}',
        width: 300,
        onSelect: function(value, data) {
            $('#vendor').val(data);
            $('#vendor-name').hide();
            $('#vendor-name').val('');
            $('#vendor-display span').html(value);
            $('#vendor-display').show();
            loading($('div.grid'));
            $('div.grid').load('${url('departments.by_vendor')}', {'uuid': data});
        },
    });

    $('#vendor-name').focus();

    $('#change-vendor').click(function() {
        $('#vendor').val('');
        $('#vendor-display').hide();
        $('#vendor-name').show();
        $('#vendor-name').focus();
        $('div.grid').empty();
    });

    $('form').submit(function() {
        var depts = [];
        $('div.grid table tbody tr').each(function() {
            if ($(this).find('td.checkbox input[type=checkbox]').is(':checked')) {
                depts.push(get_uuid(this));
            }
            $('#departments').val(depts.toString());
            return true;
        });
    });
    
});

</script>
