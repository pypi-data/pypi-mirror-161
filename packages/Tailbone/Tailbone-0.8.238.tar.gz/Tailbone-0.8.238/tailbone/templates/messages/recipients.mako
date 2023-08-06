## -*- coding: utf-8; -*-

<%def name="message_recipients_template()">
  <script type="text/x-template" id="message-recipients-template">
    <div>

      <input type="hidden" :name="name" v-model="actualValue" />

      <b-field grouped group-multiline>
        <div v-for="uuid in actualValue"
             :key="uuid"
             class="control">
          <b-tag type="is-primary"
                 attached
                 aria-close-label="Remove recipient"
                 closable
                 @close="removeRecipient(uuid)">
            {{ recipientDisplayMap[uuid] }}
          </b-tag>
        </div>
      </b-field>

      <b-autocomplete v-model="autocompleteValue"
                      placeholder="add recipient"
                      :data="filteredData"
                      field="uuid"
                      @select="selectionMade"
                      keep-first>
        <template slot-scope="props">
          {{ props.option.label }}
        </template>
        <template slot="empty">No results found</template>
      </b-autocomplete>
    </div>
  </script>
</%def>
