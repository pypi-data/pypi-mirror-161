## -*- coding: utf-8; -*-

<%def name="render_buefy_field(field, bfield_kwargs={})">
  % if form.field_visible(field.name):
      <% error_messages = form.get_error_messages(field) %>
      <b-field horizontal
               label="${form.get_label(field.name)}"
               ## TODO: is this class="file" really needed?
               % if isinstance(field.schema.typ, deform.FileData):
               class="file"
               % endif
               % if form.has_helptext(field.name):
               message="${form.render_helptext(field.name)}"
               % endif
               % if error_messages:
               type="is-danger"
               :message='${form.messages_json(error_messages)|n}'
               % endif
               ${h.HTML.render_attrs(bfield_kwargs)}
               >
        ${field.serialize(use_buefy=True)|n}
      </b-field>
  % else:
      ## hidden field
      ${field.serialize()|n}
  % endif
</%def>
