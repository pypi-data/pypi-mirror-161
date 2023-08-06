## -*- coding: utf-8; -*-
<html>
  <head>
    <title>Receiving Worksheet</title>
    <style type="text/css">
      .notes {
          margin-bottom: 2em;
      }
      .spacer {
          display: inline-block;
          width: 1em;
      }
      .receiving-info {
          padding-top: 1em;
      }
      table {
          font-size: 0.8em;
          white-space: nowrap;
      }
      th, td {
          padding: 1em 0.4em 0 0;
      }
      th {
          text-align: left;
      }
      .quantity {
          text-align: center;
      }
      .currency {
          text-align: right;
      }
    </style>
  </head>
  <body>

    <h1>Receiving Worksheet</h1>

    <p class="notes">Notes:</p>

    <p class="info">
      Vendor:&nbsp; <strong>(${purchase.vendor.id}) ${purchase.vendor}</strong>
      <span class="spacer"></span>
      Phone:&nbsp; <strong>${purchase.vendor.phone}</strong>
    </p>
    <p class="info">
      Contact:&nbsp; <strong>${purchase.vendor.contact}</strong>
      <span class="spacer"></span>
      Fax:&nbsp; <strong>${purchase.vendor.fax_number}</strong>
    </p>
    <p class="info">
      Store ID:&nbsp; <strong>${purchase.store.id}</strong>
      <span class="spacer"></span>
      Buyer:&nbsp; <strong>${purchase.buyer}</strong>
      <span class="spacer"></span>
      Order Date:&nbsp; <strong>${purchase.date_ordered}</strong>
    </p>
    <p class="receiving-info">
      Received on (date):&nbsp; ____________________
      <span class="spacer"></span>
      Received by (name):&nbsp; ____________________
    </p>

    <table>
      <thead>
        <tr>
          <th>UPC</th>
          <th>Vend Code</th>
          <th>Brand</th>
          <th>Description</th>
          <th>Cases</th>
          <th>Units</th>
          <th>Unit Cost</th>
          <th>Total Cost</th>
        </tr>
      </thead>
      <tbody>
        % for item in purchase.items:
            <tr>
              <td>${item.upc.pretty() if item.upc else item.item_id}</td>
              <td>${item.vendor_code or ''}</td>
              <td>${(item.brand_name or '')[:15]}</td>
              <td>${item.description or ''}</td>
              <td class="quantity">${h.pretty_quantity(item.cases_ordered or 0)}</td>
              <td class="quantity">${h.pretty_quantity(item.units_ordered or 0)}</td>
              <td class="currency">${'${:0,.2f}'.format(item.po_unit_cost) if item.po_unit_cost is not None else ''}</td>
              <td class="currency">${'${:0,.2f}'.format(item.po_total) if item.po_total is not None else ''}</td>
            </tr>
        % endfor
      </tbody>
    </table>

  </body>
</html>
