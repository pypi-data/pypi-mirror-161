## -*- coding: utf-8; -*-
<%inherit file="/master/index.mako" />

<%def name="grid_tools()">
  ${parent.grid_tools()}

  % if master.has_perm('collect_wild_uoms'):
  <b-button type="is-primary"
            icon-pack="fas"
            icon-left="fas fa-shopping-basket"
            @click="showingCollectWildDialog = true">
    Collect from the Wild
  </b-button>

  ${h.form(url('{}.collect_wild_uoms'.format(route_prefix)), ref='collect-wild-uoms-form')}
  ${h.csrf_token(request)}
  ${h.end_form()}

  <b-modal has-modal-card
           :active.sync="showingCollectWildDialog">
    <div class="modal-card">

      <header class="modal-card-head">
        <p class="modal-card-title">Collect from the Wild</p>
      </header>

      <section class="modal-card-body">
        <p>
          This tool will query some database(s) in order to discover all UOM
          abbreviations which currently exist in your product data.
        </p>
        <p>
          Depending on how it has to go about that, this could take a minute or
          two.&nbsp; Please be patient when running it.
        </p>
      </section>

      <footer class="modal-card-foot">
        <b-button @click="showingCollectWildDialog = false">
          Cancel
        </b-button>
        <once-button type="is-primary"
                     @click="collectFromWild()"
                     icon-left="shopping-basket"
                     text="Collect from the Wild">
        </once-button>
      </footer>

    </div>
  </b-modal>
  % endif
</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  % if master.has_perm('collect_wild_uoms'):
  <script type="text/javascript">

    TailboneGridData.showingCollectWildDialog = false

    TailboneGrid.methods.collectFromWild = function() {
        this.$refs['collect-wild-uoms-form'].submit()
    }

  </script>
  % endif
</%def>


${parent.body()}
