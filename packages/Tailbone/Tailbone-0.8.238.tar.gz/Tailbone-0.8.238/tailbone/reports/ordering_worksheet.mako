## -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html style="direction: ltr;" xmlns="http://www.w3.org/1999/xhtml" lang="en-us">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>Ordering Worksheet : ${vendor.name}</title>
    <style type="text/css">

    body {
        font-family: sans-serif;
    }

    h1 {
        font-size: 24px;
        margin: 10px 0px;
    }

    h2 {
        font-size: 20px;
        margin: 0px;
        padding: 0px;
    }

    table {
        border-bottom: 1px solid #000000;
        border-left: 1px solid #000000;
        border-collapse: collapse;
        empty-cells: show;
    }

    th {
        border-right: 1px solid #000000;
        border-top: 1px solid #000000;
        padding: 4px 8px;
    }

    th.department {
        border-left: none;
        font-size: 1.2em;
        padding: 15px;
        text-align: left;
        text-transform: uppercase;
    }

    th.subdepartment {
        border-left: none;
        padding: 15px;
        text-align: left;
    }

    td {
        border-right: 1px solid #000000;
        border-top: 1px solid #000000;
        padding: 2px 4px;
        white-space: nowrap;
    }

    td.upc,
    td.case-qty,
    td.code,
    td.preferred {
        text-align: center;
    }

    td.code {
        font-family: monospace;
        font-size: 120%;
    }

    td.scratch_pad {
        width: 20px;
    }

    td.spacer {
        height: 50px;
    }

    </style>
  </head>

  <body>
    <h1>Ordering Worksheet</h1>
    <h2>Vendor:&nbsp; ${vendor.name} (${vendor.id})</h2>
    <h2>Phone:&nbsp; ${vendor.phone or ''}</h2>
    <h2>Contact:&nbsp; ${vendor.contact or ''}</h2>
    <h3>generated on ${date} at ${time}</h3>
    <br clear="all" />

    <table>
      % for dept in sorted(costs, key=lambda x: x.name):
          <tr>
            <th class="department" colspan="21">Department:&nbsp; ${dept.name} (${dept.number})</th>
          </tr>
          % for subdept in sorted(costs[dept], key=lambda x: x.name):
              <tr>
                <th class="subdepartment" colspan="21">Subdepartment:&nbsp; ${subdept.name} (${subdept.number})</th>
              </tr>
              <tr>
                <th>UPC</th>
                <th>Brand</th>
                <th>Description</th>
                <th>Size</th>
                <th>Case</th>
                <th>Vend. Code</th>
                <th>Pref.</th>
                <th colspan="14">Order Scratch Pad</th>
              </tr>
              % for cost in sorted(costs[dept][subdept], key=cost_sort_key):
                  <tr>
                    <td class="upc">${get_upc(cost.product)}</td>
                    <td class="brand">${cost.product.brand or ''}</td>
                    <td class="desc">${cost.product.description}</td>
                    <td class="size">${cost.product.size or ''}</td>
                    <td class="case-qty">${cost.case_size} ${"LB" if cost.product.weighed else "EA"}</td>
                    <td class="code">${cost.code or ''}</td>
                    <td class="preferred">${'X' if cost.preference == 1 else ''}</td>
                    % for i in range(14):
                        <td class="scratch_pad">&nbsp;</td>
                    % endfor
                  </tr>
              % endfor
              <tr>
                <td class="spacer" colspan="21">
              </tr>
          % endfor
      % endfor
    </table>
  </body>
</html>
