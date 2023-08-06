## -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html style="direction: ltr;" xmlns="http://www.w3.org/1999/xhtml" lang="en-us">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <title>Inventory Worksheet : ${department.name}</title>
    <style type="text/css">

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
        width: 100%;
    }

    th {
        border-right: 1px solid #000000;
        border-top: 1px solid #000000;
        padding: 4px 8px;
    }

    th.subdepartment {
        border-left: none;
        font-size: 1.2em;
        padding: 15px;
        text-align: left;
    }

    td {
        border-right: 1px solid #000000;
        border-top: 1px solid #000000;
        padding: 2px 4px;
        white-space: nowrap;
    }

    td.upc {
        text-align: center;
    }

    td.count {
        width: 25%;
    }

    td.spacer {
        height: 50px;
    }

    </style>
  </head>

  <body>
    <h1>Inventory Worksheet</h1>
    <h2>Department:&nbsp; ${department.name} (${department.number})</h2>
    <h3>generated on ${date} at ${time}</h3>
    <br clear="all" />

    <table>
      % for subdepartment in department.subdepartments:
          <% products = get_products(subdepartment) %>
          % if products:
              <tr>
                <th class="subdepartment" colspan="4">Subdepartment:&nbsp; ${subdepartment.name} (${subdepartment.number})</th>
              </tr>
              <tr>
                <th>UPC</th>
                <th>Brand</th>
                <th>Description</th>
                <th>Count</th>
              </tr>
              % for product in products:
                  <tr>
                    <td class="upc">${get_upc(product)}</td>
                    <td class="brand">${product.brand or ''}</td>
                    <td class="description">${product.description} ${product.size}</td>
                    <td class="count">&nbsp;</td>
                  </tr>
              % endfor
              <tr>
                <td class="spacer" colspan="19">
              </tr>
          % endif
      % endfor
    </table>
  </body>
</html>
