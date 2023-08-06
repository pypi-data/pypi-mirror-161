## -*- coding: utf-8; -*-
<%inherit file="/master/view.mako" />

<%def name="render_form_buttons()">
  <div v-if="!showUploadForm" class="buttons">
    % if master.has_perm('replace'):
    <b-button type="is-primary"
              @click="showUploadForm = true">
      Upload Replacement Module
    </b-button>
    % endif
    <once-button type="is-primary"
                 tag="a"
                 % if instance.get('error'):
                 href="#" disabled
                 % else:
                 href="${url('generate_specific_report', type_key=instance['report'].type_key)}"
                 % endif
                 text="Generate this Report">
    </once-button>
  </div>
  % if master.has_perm('replace'):
  <div v-if="showUploadForm">
    ${h.form(master.get_action_url('replace', instance), enctype='multipart/form-data', **{'@submit': 'uploadSubmitting = true'})}
    ${h.csrf_token(request)}
    <b-field label="New Module File" horizontal>

      <b-field class="file is-primary"
               :class="{'has-name': !!uploadFile}"
               >
        <b-upload name="replacement_module"
                  v-model="uploadFile"
                  class="file-label">
          <span class="file-cta">
            <b-icon class="file-icon" pack="fas" icon="upload"></b-icon>
            <span class="file-label">Click to upload</span>
          </span>
        </b-upload>
        <span v-if="uploadFile"
              class="file-name">
          {{ uploadFile.name }}
        </span>
      </b-field>

      <div class="buttons">
        <b-button @click="showUploadForm = false">
          Cancel
        </b-button>
        <b-button type="is-primary"
                  native-type="submit"
                  :disabled="uploadSubmitting || !uploadFile"
                  icon-pack="fas"
                  icon-left="save">
          {{ uploadSubmitting ? "Working, please wait..." : "Save" }}
        </b-button>
      </div>

    </b-field>
    ${h.end_form()}
  </div>
  % endif
  <br />
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if master.has_perm('replace'):
  <script type="text/javascript">

    ${form.component_studly}Data.showUploadForm = false

    ${form.component_studly}Data.uploadFile = null

    ${form.component_studly}Data.uploadSubmitting = false

  </script>
  % endif
</%def>

${parent.body()}
