
const TailboneAutocomplete = {

    template: '#tailbone-autocomplete-template',

    props: {

        // this is the "input" field name essentially.  primarily is
        // useful for "traditional" tailbone forms; it normally is not
        // used otherwise.  it is passed as-is to the buefy
        // autocomplete component `name` prop
        name: String,

        // the url from which search results are to be obtained.  the
        // url should expect a GET request with a query string with a
        // single `term` parameter, and return results as a JSON array
        // containing objects with `value` and `label` properties.
        serviceUrl: String,

        // callers do not specify this directly but rather by way of
        // the `v-model` directive.  this component will emit `input`
        // events when the value changes
        value: String,

        // callers may set an initial label if needed.  this is useful
        // in cases where the autocomplete needs to "already have a
        // value" on page load.  for instance when a user fills out
        // the autocomplete field, but leaves other required fields
        // blank and submits the form; page will re-load showing
        // errors but the autocomplete field should remain "set" -
        // normally it is only given a "value" (e.g. uuid) but this
        // allows for the "label" to display correctly as well
        initialLabel: String,

        // while the `initialLabel` above is useful for setting the
        // *initial* label (of course), it cannot be used to
        // arbitrarily update the label during the component's life.
        // if you do need to *update* the label after initial page
        // load, then you should set `assignedLabel` instead.  one
        // place this happens is in /custorders/create page, where
        // product autocomplete shows some results, and user clicks
        // one, but then handler logic can forcibly "swap" the
        // selection, causing *different* product data to come back
        // from the server, and autocomplete label should be updated
        // to match.  this feels a bit awkward still but does work..
        assignedLabel: String,

        // simple placeholder text for the input box
        placeholder: String,

        // TODO: pretty sure this can be ignored..?
        // (should deprecate / remove if so)
        assignedValue: String,
    },

    data() {

        // we want to track the "currently selected option" - which
        // should normally be `null` to begin with, unless we were
        // given a value, in which case we use `initialLabel` to
        // complete the option
        let selected = null
        if (this.value) {
            selected = {
                value: this.value,
                label: this.initialLabel,
            }
        }

        return {

            // this contains the search results; its contents may
            // change over time as new searches happen.  the
            // "currently selected option" should be one of these,
            // unless it is null
            data: [],

            // this tracks our "currently selected option" - per above
            selected: selected,

            // since we are wrapping a component which also makes use
            // of the "value" paradigm, we must separate the concerns.
            // so we use our own `value` prop to interact with the
            // caller, but then we use this `buefyValue` data point to
            // communicate with the buefy autocomplete component.
            // note that `this.value` will always be either a uuid or
            // null, whereas `this.buefyValue` may be raw text as
            // entered by the user.
            buefyValue: this.value,

            // // TODO: we are "setting" this at the appropriate time,
            // // but not clear if that actually affects anything.
            // // should we just remove it?
            // isFetching: false,
        }
    },

    // watch: {
    //     // TODO: yikes this feels hacky.  what happens is, when the
    //     // caller explicitly assigns a new UUID value to the tailbone
    //     // autocomplate component, the underlying buefy autocomplete
    //     // component was not getting the new value.  so here we are
    //     // explicitly making sure it is in sync.  this issue was
    //     // discovered on the "new vendor catalog batch" page
    //     value(val) {
    //         this.$nextTick(() => {
    //             if (this.buefyValue != val) {
    //                 this.buefyValue = val
    //             }
    //         })
    //     },
    // },

    methods: {

        // fetch new search results from the server.  this is invoked
        // via the `@typing` event from buefy autocomplete component.
        // the doc at https://buefy.org/documentation/autocomplete
        // mentions `debounce` as being optional. at one point i
        // thought it would fix a performance bug; not sure `debounce`
        // helped but figured might as well leave it
        getAsyncData: debounce(function (entry) {

            // since the `@typing` event from buefy component does not
            // "self-regulate" in any way, we a) use `debounce` above,
            // but also b) skip the search unless we have at least 3
            // characters of input from user
            if (entry.length < 3) {
                this.data = []
                return
            }

            // and perform the search
            this.$http.get(this.serviceUrl + '?term=' + encodeURIComponent(entry))
                .then(({ data }) => {
                    this.data = data
                })
                .catch((error) => {
                    this.data = []
                    throw error
                })
        }),

        // this method is invoked via the `@select` event of the buefy
        // autocomplete component.  the `option` received will either
        // be `null` or else a simple object with (at least) `value`
        // and `label` properties
        selectionMade(option) {

            // we want to keep track of the "currently selected
            // option" so we can display its label etc.  also this
            // helps control the visibility of the autocomplete input
            // field vs. the button which indicates the field has a
            // value
            this.selected = option

            // reset the internal value for buefy autocomplete
            // component.  note that this value will normally hold
            // either the raw text entered by the user, or a uuid.  we
            // will not be needing either of those b/c they are not
            // visible to user once selection is made, and if the
            // selection is cleared we want user to start over anyway
            this.buefyValue = null

            // here is where we alert callers to the new value
            if (option) {
                this.$emit('new-label', option.label)
            }
            this.$emit('input', option ? option.value : null)
        },

        // set selection to the given option, which should a simple
        // object with (at least) `value` and `label` properties
        setSelection(option) {
            this.$refs.autocomplete.setSelected(option)
        },

        // clear the field of any value, i.e. set the "currently
        // selected option" to null.  this is invoked when you click
        // the button, which is visible while the field has a value.
        // but callers can invoke it directly as well.
        clearSelection(focus) {

            // clear selection for the buefy autocomplete component
            this.$refs.autocomplete.setSelected(null)

            // maybe set focus to our (autocomplete) component
            if (focus) {
                this.$nextTick(function() {
                    this.focus()
                })
            }
        },

        // set focus to this component, which will just set focus to
        // the buefy autocomplete component
        focus() {
            this.$refs.autocomplete.focus()
        },

        // this determines the "display text" for the button, which is
        // shown when a selection has been made (or rather, when the
        // field actually has a value)
        getDisplayText() {

            // always use the "assigned" label if we have one
            // TODO: where is this used?  what is the use case?
            if (this.assignedLabel) {
                return this.assignedLabel
            }

            // if we have a "currently selected option" then use its
            // label.  all search results / options have a `label`
            // property as that is shown directly in the autocomplete
            // dropdown.  but if the option also has a `display`
            // property then that is what we will show in the button.
            // this way search results can show one thing in the
            // search dropdown, and another in the button.
            if (this.selected) {
                return this.selected.display || this.selected.label
            }

            // we have nothing to go on here..
            return ""
        },

        // returns the "raw" user input from the underlying buefy
        // autocomplete component
        getUserInput() {
            return this.buefyValue
        },
    },
}

Vue.component('tailbone-autocomplete', TailboneAutocomplete)
