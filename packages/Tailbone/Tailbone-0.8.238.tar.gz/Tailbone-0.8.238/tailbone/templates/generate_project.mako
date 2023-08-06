## -*- coding: utf-8; -*-
<%inherit file="/page.mako" />

<%def name="title()">Generate Project</%def>

<%def name="content_title()"></%def>

<%def name="page_content()">
  <b-field horizontal label="Project Type">
    <b-select v-model="projectType">
      <option value="rattail">rattail</option>
      <option value="rattail_integration">rattail-integration</option>
      <option value="tailbone_integration">tailbone-integration</option>
      ## <option value="byjove">byjove</option>
      <option value="fabric">fabric</option>
    </b-select>
  </b-field>

  <div v-if="projectType == 'rattail'">
    ${h.form(request.current_route_url(), ref='rattailForm')}
    ${h.csrf_token(request)}
    ${h.hidden('project_type', value='rattail')}
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Naming</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Name"
                   message="The &quot;canonical&quot; name generally used to refer to this project">
            <b-input name="name" v-model="rattail.name"></b-input>
          </b-field>

          <b-field horizontal label="Slug"
                   message="Used for e.g. naming the project source code folder">
            <b-input name="slug" v-model="rattail.slug"></b-input>
          </b-field>

          <b-field horizontal label="Organization"
                   message="For use with &quot;branding&quot; etc.">
            <b-input name="organization" v-model="rattail.organization"></b-input>
          </b-field>

          <b-field horizontal label="Package Name for PyPI"
                   message="It&apos;s a good idea to use org name as namespace prefix here">
            <b-input name="python_project_name" v-model="rattail.python_project_name"></b-input>
          </b-field>

          <b-field horizontal label="Package Name in Python"
                   :message="`For example, ~/src/${'$'}{rattail.slug}/${'$'}{rattail.python_package_name}/__init__.py`">
            <b-input name="python_name" v-model="rattail.python_package_name"></b-input>
          </b-field>

        </div>
      </div>
    </div>
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Database</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Has Rattail DB"
                   message="Note that a DB is required for the Web App">
            <b-checkbox name="has_db"
                        v-model="rattail.has_rattail_db"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Extends Rattail DB Schema"
                   message="For adding custom tables/columns to the core schema">
            <b-checkbox name="extends_db"
                        v-model="rattail.extends_rattail_db_schema"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Uses Rattail Batch Schema"
                   v-show="false"
                   message="Needed for &quot;dynamic&quot; (e.g. import/export) batches">
            <b-checkbox name="has_batch_schema"
                        v-model="rattail.uses_rattail_batch_schema"
                        native-value="true">
            </b-checkbox>
          </b-field>

        </div>
      </div>
    </div>
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Web App</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Has Tailbone Web App">
            <b-checkbox name="has_web"
                        v-model="rattail.has_tailbone_web_app"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Has Tailbone Web API"
                   v-show="false"
                   message="Needed for e.g. Vue.js SPA mobile apps">
            <b-checkbox name="has_web_api"
                        v-model="rattail.has_tailbone_web_api"
                        native-value="true">
            </b-checkbox>
          </b-field>

        </div>
      </div>
    </div>
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Integrations</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Integrates w/ Catapult"
                   message="Add schema, import/export logic etc. for ECRS Catapult">
            <b-checkbox name="integrates_catapult"
                        v-model="rattail.integrates_with_catapult"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Integrates w/ CORE-POS"
                   v-show="false">
            <b-checkbox name="integrates_corepos"
                        v-model="rattail.integrates_with_corepos"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Integrates w/ LOC SMS"
                   message="Add schema, import/export logic etc. for LOC SMS">
            <b-checkbox name="integrates_locsms"
                        v-model="rattail.integrates_with_locsms"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Has DataSync Service"
                   v-show="false">
            <b-checkbox name="has_datasync"
                        v-model="rattail.has_datasync_service"
                        native-value="true">
            </b-checkbox>
          </b-field>

        </div>
      </div>
    </div>
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Deployment</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Uses Fabric">
            <b-checkbox name="uses_fabric"
                        v-model="rattail.uses_fabric"
                        native-value="true">
            </b-checkbox>
          </b-field>

        </div>
      </div>
    </div>
    ${h.end_form()}
  </div>

  <div v-if="projectType == 'rattail_integration'">
    ${h.form(request.current_route_url(), ref='rattail_integrationForm')}
    ${h.csrf_token(request)}
    ${h.hidden('project_type', value='rattail_integration')}
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Naming</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Integration Name"
                   message="Name of the system to be integrated">
            <b-input name="integration_name" v-model="rattail_integration.integration_name"></b-input>
          </b-field>

          <b-field horizontal label="Integration URL"
                   message="Reference URL for the system to be integrated">
            <b-input name="integration_url" v-model="rattail_integration.integration_url"></b-input>
          </b-field>

          <b-field horizontal label="Package Name for PyPI"
                   message="Also will be used as slug, e.g. for folder name">
            <b-input name="python_project_name" v-model="rattail_integration.python_project_name"></b-input>
          </b-field>

          ${h.hidden('slug', **{'v-model': 'rattail_integration.python_project_name'})}

          <b-field horizontal label="Package Name in Python"
                   :message="`For example, ~/src/${'$'}{rattail_integration.python_project_name}/${'$'}{rattail_integration.python_package_name}/__init__.py`">
            <b-input name="python_name" v-model="rattail_integration.python_package_name"></b-input>
          </b-field>

        </div>
      </div>
    </div>
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Options</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Extends Config"
                   message="Adds custom config extension">
            <b-checkbox name="extends_config"
                        v-model="rattail_integration.extends_config"
                        native-value="true">
            </b-checkbox>
          </b-field>

          <b-field horizontal label="Extends Rattail Schema"
                   message="Adds custom tables/columns to the Rattail DB schema">
            <b-checkbox name="extends_db"
                        v-model="rattail_integration.extends_db"
                        native-value="true">
            </b-checkbox>
          </b-field>

        </div>
      </div>
    </div>
    ${h.end_form()}
  </div>

  <div v-if="projectType == 'tailbone_integration'">
    ${h.form(request.current_route_url(), ref='tailbone_integrationForm')}
    ${h.csrf_token(request)}
    ${h.hidden('project_type', value='tailbone_integration')}
    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Naming</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Integration Name"
                   message="Name of the system to be integrated">
            <b-input name="integration_name" v-model="tailbone_integration.integration_name"></b-input>
          </b-field>

          <b-field horizontal label="Integration URL"
                   message="Reference URL for the system to be integrated">
            <b-input name="integration_url" v-model="tailbone_integration.integration_url"></b-input>
          </b-field>

          <b-field horizontal label="Package Name for PyPI"
                   message="Also will be used as slug, e.g. for folder name">
            <b-input name="python_project_name" v-model="tailbone_integration.python_project_name"></b-input>
          </b-field>

          ${h.hidden('slug', **{'v-model': 'tailbone_integration.python_project_name'})}

          <b-field horizontal label="Package Name in Python"
                   :message="`For example, ~/src/${'$'}{tailbone_integration.python_project_name}/${'$'}{tailbone_integration.python_package_name}/__init__.py`">
            <b-input name="python_name" v-model="tailbone_integration.python_package_name"></b-input>
          </b-field>

        </div>
      </div>
    </div>
    ${h.end_form()}
  </div>

  <div v-if="projectType == 'byjove'">
    ${h.form(request.current_route_url(), ref='byjoveForm')}
    ${h.csrf_token(request)}
    ${h.hidden('project_type', value='byjove')}

    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Naming</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Name">
            <b-input name="name" v-model="byjove.name"></b-input>
          </b-field>

          <b-field horizontal label="Slug">
            <b-input name="slug" v-model="byjove.slug"></b-input>
          </b-field>

        </div>
      </div>
    </div>

    ${h.end_form()}
  </div>

  <div v-if="projectType == 'fabric'">
    ${h.form(request.current_route_url(), ref='fabricForm')}
    ${h.csrf_token(request)}
    ${h.hidden('project_type', value='fabric')}

    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Naming</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Name"
                   message="The &quot;canonical&quot; name generally used to refer to this project">
            <b-input name="name" v-model="fabric.name"></b-input>
          </b-field>

          <b-field horizontal label="Slug"
                   message="Used for e.g. naming the project source code folder">
            <b-input name="slug" v-model="fabric.slug"></b-input>
          </b-field>

          <b-field horizontal label="Organization"
                   message="For use with &quot;branding&quot; etc.">
            <b-input name="organization" v-model="fabric.organization"></b-input>
          </b-field>

          <b-field horizontal label="Package Name for PyPI"
                   message="It&apos;s a good idea to use org name as namespace prefix here">
            <b-input name="python_project_name" v-model="fabric.python_project_name"></b-input>
          </b-field>

          <b-field horizontal label="Package Name in Python"
                   :message="`For example, ~/src/${'$'}{fabric.slug}/${'$'}{fabric.python_package_name}/__init__.py`">
            <b-input name="python_name" v-model="fabric.python_package_name"></b-input>
          </b-field>

        </div>
      </div>
    </div>

    <br />
    <div class="card">
      <header class="card-header">
        <p class="card-header-title">Theo</p>
      </header>
      <div class="card-content">
        <div class="content">

          <b-field horizontal label="Integrates With"
                   message="Which POS system should Theo integrate with, if any">
            <b-select name="integrates_with" v-model="fabric.integrates_with">
              <option value="">(nothing)</option>
              <option value="catapult">ECRS Catapult</option>
              <option value="corepos">CORE-POS</option>
              ## <option value="locsms">LOC SMS</option>
            </b-select>
          </b-field>

        </div>
      </div>
    </div>

    ${h.end_form()}
  </div>

  <br />
  <div class="buttons" style="padding-left: 8rem;">
    <b-button type="is-primary"
              @click="submitProjectForm()">
      Generate Project
    </b-button>
  </div>

</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.projectType = 'rattail'

    ThisPageData.rattail = {
        name: "Okay-Then",
        slug: "okay-then",
        organization: "Acme Foods",
        python_project_name: "Acme-Okay-Then",
        python_package_name: "okay_then",
        has_rattail_db: true,
        extends_rattail_db_schema: true,
        uses_rattail_batch_schema: false,
        has_tailbone_web_app: true,
        has_tailbone_web_api: false,
        has_datasync_service: false,
        integrates_with_catapult: false,
        integrates_with_corepos: false,
        integrates_with_locsms: false,
        uses_fabric: true,
    }

    ThisPageData.rattail_integration = {
        integration_name: "Foo",
        integration_url: "https://www.example.com/",
        python_project_name: "rattail-foo",
        python_package_name: "rattail_foo",
        extends_config: true,
        extends_db: true,
    }

    ThisPageData.tailbone_integration = {
        integration_name: "Foo",
        integration_url: "https://www.example.com/",
        python_project_name: "tailbone-foo",
        python_package_name: "tailbone_foo",
    }

    ThisPageData.byjove = {
        name: "Okay-Then-Mobile",
        slug: "okay-then-mobile",
    }

    ThisPageData.fabric = {
        name: "AcmeFab",
        slug: "acmefab",
        organization: "Acme Foods",
        python_project_name: "Acme-Fabric",
        python_package_name: "acmefab",
        integrates_with: '',
    }

    ThisPage.methods.submitProjectForm = function() {
        let form = this.$refs[this.projectType + 'Form']
        form.submit()
    }

  </script>
</%def>


${parent.body()}
