## -*- coding: utf-8; -*-
<%inherit file="/base.mako" />

<%def name="context_menu_items()"></%def>

<%def name="page_content()"></%def>

<%def name="render_this_page()">
  <div style="display: flex;">

    <div class="this-page-content" style="flex-grow: 1;">
      ${self.page_content()}
    </div>

    <ul id="context-menu">
      ${self.context_menu_items()}
    </ul>

  </div>
</%def>

<%def name="render_this_page_template()">
  <script type="text/x-template" id="this-page-template">
    <div>
      ${self.render_this_page()}
    </div>
  </script>
</%def>

<%def name="declare_this_page_vars()">
  <script type="text/javascript">

    let ThisPage = {
        template: '#this-page-template',
        mixins: [FormPosterMixin],
        computed: {},
        methods: {},
    }

    let ThisPageData = {
        ## TODO: should find a better way to handle CSRF token
        csrftoken: ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n},
    }

  </script>
</%def>

<%def name="modify_this_page_vars()">
  ## NOTE: if you override this, must use <script> tags
</%def>

<%def name="finalize_this_page_vars()">
  ## NOTE: if you override this, must use <script> tags
</%def>

<%def name="make_this_page_component()">
  ${self.declare_this_page_vars()}
  ${self.modify_this_page_vars()}
  ${self.finalize_this_page_vars()}

  <script type="text/javascript">

    ThisPage.data = function() { return ThisPageData }

    Vue.component('this-page', ThisPage)

  </script>
</%def>


% if use_buefy:
    ${self.render_this_page_template()}
    ${self.make_this_page_component()}
% else:
    ${self.render_this_page()}
% endif
