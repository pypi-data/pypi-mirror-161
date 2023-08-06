## -*- coding: utf-8; -*-
<%inherit file="/configure.mako" />

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    .topmenu-dropper {
        min-width: 0.8rem;
    }
    .topmenu-dropper:-moz-drag-over {
        background-color: blue;
    }
  </style>
</%def>

<%def name="form_content()">
  ${h.hidden('menus', **{':value': 'JSON.stringify(allMenuData)'})}

  <h3 class="is-size-3">Top-Level Menus</h3>
  <p class="block">Click on a menu to edit.&nbsp; Drag things around to rearrange.</p>

  <b-field grouped>

    <b-field grouped v-for="key in menuSequence"
             :key="key">
      <span class="topmenu-dropper control"
            @dragover.prevent
            @dragenter.prevent
            @drop="dropMenu($event, key)">
        &nbsp;
      </span>
      <b-button :type="editingMenu && editingMenu.key == key ? 'is-primary' : null"
                class="control"
                @click="editMenu(key)"
                :disabled="editingMenu && editingMenu.key != key"
                :draggable="!editingMenu"
                @dragstart.native="topMenuStartDrag($event, key)">
        {{ allMenus[key].title }}
      </b-button>
    </b-field>

    <div class="topmenu-dropper control"
         @dragover.prevent
         @dragenter.prevent
         @drop="dropMenu($event, '_last_')">
      &nbsp;
    </div>
    <b-button v-show="!editingMenu"
              type="is-primary"
              icon-pack="fas"
              icon-left="plus"
              @click="editMenuNew()">
      Add
    </b-button>

  </b-field>

  <div v-if="editingMenu"
       style="max-width: 40%;">

    <b-field grouped>
    
      <b-field label="Label">
        <b-input v-model="editingMenu.title"
                 ref="editingMenuTitleInput">
        </b-input>
      </b-field>

      <b-field label="Actions">
        <div class="buttons">
          <b-button icon-pack="fas"
                    icon-left="redo"
                    @click="editMenuCancel()">
            Revert / Cancel
          </b-button>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    @click="editMenuSave()">
            Save
          </b-button>
          <b-button type="is-danger"
                    icon-pack="fas"
                    icon-left="trash"
                    @click="editMenuDelete()">
            Delete
          </b-button>
        </div>
      </b-field>

    </b-field>

    <b-field>
      <template #label>
        <span style="margin-right: 2rem;">Menu Items</span>
        <b-button type="is-primary"
                  icon-pack="fas"
                  icon-left="plus"
                  @click="editMenuItemInitDialog()">
          Add
        </b-button>
      </template>
      <ul class="list">
        <li v-for="item in editingMenu.items"
            class="list-item"
            draggable
            @dragstart="menuItemStartDrag($event, item)"
            @dragover.prevent
            @dragenter.prevent
            @drop="menuItemDrop($event, item)">
          <span :class="item.type == 'sep' ? 'has-text-info' : null">
            {{ item.type == 'sep' ? "-- separator --" : item.title }}
          </span>
          <span class="is-pulled-right grid-action">
            <a href="#" @click.prevent="editMenuItemInitDialog(item)">
              <i class="fas fa-edit"></i>
              Edit
            </a>
            &nbsp;
           <a href="#" class="has-text-danger"
              @click.prevent="editMenuItemDelete(item)">
              <i class="fas fa-trash"></i>
              Delete
            </a>
            &nbsp;
          </span>
        </li>
      </ul>
    </b-field>

    <b-modal has-modal-card
             :active.sync="editMenuItemShowDialog">
      <div class="modal-card">

        <header class="modal-card-head">
          <p class="modal-card-title">{{ editingMenuItem.isNew ? "Add" : "Edit" }} Item</p>
        </header>

        <section class="modal-card-body">

          <b-field label="Item Type">
            <b-select v-model="editingMenuItem.type">
              <option value="item">Route Link</option>                      
              <option value="sep">Separator</option>                      
            </b-select>
          </b-field>

          <b-field label="Route"
                   v-show="editingMenuItem.type == 'item'">
            <b-select v-model="editingMenuItem.route"
                      @input="editingMenuItemRouteChanged">
              <option v-for="route in editMenuIndexRoutes"
                      :key="route.route"
                      :value="route.route">
                {{ route.label }}
              </option>                      
            </b-select>
          </b-field>

          <b-field label="Label"
                   v-show="editingMenuItem.type == 'item'">
            <b-input v-model="editingMenuItem.title">
            </b-input>
          </b-field>

        </section>

        <footer class="modal-card-foot">
          <b-button @click="editMenuItemShowDialog = false">
            Cancel
          </b-button>
          <b-button type="is-primary"
                    icon-pack="fas"
                    icon-left="save"
                    :disabled="editMenuItemSaveDisabled"
                    @click="editMenuSaveItem()">
            Save
          </b-button>
        </footer>
      </div>
    </b-modal>

  </div>

</%def>

<%def name="modify_this_page_vars()">
  ${parent.modify_this_page_vars()}
  <script type="text/javascript">

    ThisPageData.menuSequence = ${json.dumps([m['key'] for m in menus])|n}

    ThisPageData.allMenus = {}
    % for topitem in menus:
        ThisPageData.allMenus['${topitem['key']}'] = ${json.dumps(topitem)|n}
    % endfor

    ThisPageData.editMenuIndexRoutes = ${json.dumps(index_route_options)|n}

    ThisPageData.editingMenu = null
    ThisPageData.editingMenuItem = {isNew: true}
    ThisPageData.editingMenuItemIndex = null

    ThisPageData.editMenuItemShowDialog = false

    // nb. this value is sent on form submit
    ThisPage.computed.allMenuData = function() {
        let menus = []
        for (key of this.menuSequence) {
            menus.push(this.allMenus[key])
        }
        return menus
    }

    ThisPage.methods.editMenu = function(key) {
        if (this.editingMenu) {
            return
        }

        // copy existing (original) menu to be edited
        let original = this.allMenus[key]
        this.editingMenu = {
            key: key,
            title: original.title,
            items: [],
        }

        // and copy each item separately
        for (let item of original.items) {
            this.editingMenu.items.push({
                key: item.key,
                title: item.title,
                route: item.route,
                url: item.url,
                perm: item.perm,
                type: item.type,
            })
        }
    }

    ThisPage.methods.editMenuNew = function() {

        // editing brand new menu
        this.editingMenu = {items: []}

        // focus title input
        this.$nextTick(() => {
            this.$refs.editingMenuTitleInput.focus()
        })
    }

    ThisPage.methods.editMenuCancel = function(key) {
        this.editingMenu = null
    }

    ThisPage.methods.editMenuSave = function() {

        let key = this.editingMenu.key
        if (key) {

            // update existing (original) menu with user edits
            this.allMenus[key] = this.editingMenu

        } else {

            // generate makeshift key
            key = this.editingMenu.title.replace(/\W/g, '')

            // add new menu to data set
            this.allMenus[key] = this.editingMenu
            this.menuSequence.push(key)
        }

        // no longer editing
        this.editingMenu = null
        this.settingsNeedSaved = true
    }

    ThisPage.methods.editMenuDelete = function() {

        if (confirm("Really delete this menu?")) {
            let key = this.editingMenu.key

            // remove references from primary collections
            let i = this.menuSequence.indexOf(key)
            this.menuSequence.splice(i, 1)
            delete this.allMenus[key]

            // no longer editing
            this.editingMenu = null
            this.settingsNeedSaved = true
        }
    }

    ## TODO: see also https://learnvue.co/2020/01/how-to-add-drag-and-drop-to-your-vuejs-project/#adding-drag-and-drop-functionality

    ## TODO: see also https://developer.mozilla.org/en-US/docs/Web/API/HTML_Drag_and_Drop_API

    ## TODO: maybe try out https://www.npmjs.com/package/vue-drag-drop

    ThisPage.methods.topMenuStartDrag = function(event, key) {
        event.dataTransfer.setData('key', key)
    }

    ThisPage.methods.dropMenu = function(event, target) {
        let key = event.dataTransfer.getData('key')
        if (target == key) {
            return              // same target
        }

        let i = this.menuSequence.indexOf(key)
        let j = this.menuSequence.indexOf(target)
        if (i + 1 == j) {
            return              // same target
        }

        if (target == '_last_') {
            if (this.menuSequence[this.menuSequence.length-1] != key) {
                this.menuSequence.splice(i, 1)
                this.menuSequence.push(key)
                this.settingsNeedSaved = true
            }
        } else {
            this.menuSequence.splice(i, 1)
            j = this.menuSequence.indexOf(target)
            this.menuSequence.splice(j, 0, key)
            this.settingsNeedSaved = true
        }
    }

    ThisPage.methods.menuItemStartDrag = function(event, item) {
        let i = this.editingMenu.items.indexOf(item)
        event.dataTransfer.setData('itemIndex', i)
    }

    ThisPage.methods.menuItemDrop = function(event, item) {
        let oldIndex = event.dataTransfer.getData('itemIndex')
        let pruned = this.editingMenu.items.splice(oldIndex, 1)
        let newIndex = this.editingMenu.items.indexOf(item)
        this.editingMenu.items.splice(newIndex, 0, pruned[0])
    }

    ThisPage.methods.editMenuItemInitDialog = function(item) {

        if (item === undefined) {
            this.editingMenuItemIndex = null

            // create new item to edit
            this.editingMenuItem = {
                isNew: true,
                route: null,
                title: null,
                perm: null,
                type: 'item',
            }

        } else {
            this.editingMenuItemIndex = this.editingMenu.items.indexOf(item)

            // copy existing (original item to be edited
            this.editingMenuItem = {
                key: item.key,
                title: item.title,
                route: item.route,
                url: item.url,
                perm: item.perm,
                type: item.type,
            }
        }

        this.editMenuItemShowDialog = true
    }

    ThisPage.methods.editingMenuItemRouteChanged = function(routeName) {
        for (let route of this.editMenuIndexRoutes) {
            if (route.route == routeName) {
                this.editingMenuItem.title = route.label
                this.editingMenuItem.perm = route.perm
                break
            }
        }
    }

    ThisPage.computed.editMenuItemSaveDisabled = function() {
        if (this.editingMenuItem.type == 'item') {
            if (!this.editingMenuItem.route) {
                return true
            }
            if (!this.editingMenuItem.title) {
                return true
            }
        }
        return false
    }

    ThisPage.methods.editMenuSaveItem = function() {

        if (this.editingMenuItem.isNew) {
            this.editingMenu.items.push(this.editingMenuItem)

        } else {
            this.editingMenu.items.splice(this.editingMenuItemIndex,
                                          1,
                                          this.editingMenuItem)
        }

        this.editMenuItemShowDialog = false
    }

    ThisPage.methods.editMenuItemDelete = function(item) {

        if (confirm("Really delete this item?")) {

            // remove item from editing menu
            let i = this.editingMenu.items.indexOf(item)
            this.editingMenu.items.splice(i, 1)
        }
    }

  </script>
</%def>


${parent.body()}
