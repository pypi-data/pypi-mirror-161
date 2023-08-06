## -*- coding: utf-8 -*-
<%inherit file="/master/view.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/purchases.css'))}
</%def>

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  % if instance.status < enum.PURCHASE_STATUS_RECEIVED and request.has_perm('purchases.receiving_worksheet'):
      <li>${h.link_to("Print Receiving Worksheet", url('purchases.receiving_worksheet', uuid=instance.uuid), target='_blank')}</li>
  % endif
</%def>

${parent.body()}
