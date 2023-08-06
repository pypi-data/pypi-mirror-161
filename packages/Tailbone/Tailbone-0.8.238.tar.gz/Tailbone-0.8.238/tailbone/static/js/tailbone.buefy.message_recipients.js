
const MessageRecipients = {
    template: '#message-recipients-template',

    props: {
        name: String,
        value: Array,
        possibleRecipients: Array,
        recipientDisplayMap: Object,
    },

    data() {
        return {
            autocompleteValue: null,
            actualValue: this.value,
        }
    },

    computed: {

        filteredData() {
            // this is the logic responsible for "matching" user's autocomplete
            // input, with possible recipients.  we return all matches as list.
            let filtered = []
            if (this.autocompleteValue) {
                let term = this.autocompleteValue.toLowerCase()
                this.possibleRecipients.forEach(function(value, key, map) {

                    // first check to see if value is simple string, if so then
                    // will attempt to match it directly
                    if (value.toLowerCase !== undefined) {
                        if (value.toLowerCase().indexOf(term) >= 0) {
                            filtered.push({value: key, label: value})
                        }

                    } else {
                        // value is not a string, which means it must be a
                        // grouping object, which must have a name property
                        if (value.name.toLowerCase().indexOf(term) >= 0) {
                            filtered.push({
                                value: key,
                                label: value.name,
                                moreValues: value.uuids,
                            })
                        }
                    }
                })
            }
            return filtered
        },
    },

    methods: {

        addRecipient(uuid) {

            // add selected user to "actual" value
            if (!this.actualValue.includes(uuid)) {
                this.actualValue.push(uuid)
            }
        },

        removeRecipient(uuid) {

            // locate and remove user uuid from "actual" value
            for (let i = 0; i < this.actualValue.length; i++) {
                if (this.actualValue[i] == uuid) {
                    this.actualValue.splice(i, 1)
                    break
                }
            }
        },

        selectionMade(option) {

            // apparently option can be null sometimes..?
            if (option) {

                // add all newly-selected users to "actual" value
                if (option.moreValues) {
                    // grouping object; add all its "contained" values
                    option.moreValues.forEach(function(uuid) {
                        this.addRecipient(uuid)
                    }, this)
                } else {
                    // normal object, just add its value
                    this.addRecipient(option.value)
                }

                // let parent know we changed value
                this.$emit('input', this.actualValue)
            }

            // clear out the *visible* autocomplete value
            this.$nextTick(function() {
                this.autocompleteValue = null

                // TODO: wtf, sometimes we have to clear this out twice?!
                this.$nextTick(function() {
                    this.autocompleteValue = null
                })
            })
        },
    },
}


Vue.component('message-recipients', MessageRecipients)
