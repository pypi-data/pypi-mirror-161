
const GridFilterDateValue = {
    template: '#grid-filter-date-value-template',
    props: {
        value: String,
        dateRange: Boolean,
    },
    data() {
        return {
            startDate: null,
            endDate: null,
        }
    },
    mounted() {
        if (this.dateRange) {
            if (this.value.includes('|')) {
                let values = this.value.split('|')
                if (values.length == 2) {
                    this.startDate = values[0]
                    this.endDate = values[1]
                } else {
                    this.startDate = this.value
                }
            } else {
                this.startDate = this.value
            }
        } else {
            this.startDate = this.value
        }
    },
    methods: {
        focus() {
            this.$refs.startDate.focus()
        },
        startDateChanged(value) {
            if (this.dateRange) {
                value += '|' + this.endDate
            }
            this.$emit('input', value)
        },
        endDateChanged(value) {
            value = this.startDate + '|' + value
            this.$emit('input', value)
        },
    },
}

Vue.component('grid-filter-date-value', GridFilterDateValue)


const GridFilter = {
    template: '#grid-filter-template',
    props: {
        filter: Object
    },

    methods: {

        changeVerb() {
            // set focus to value input, "as quickly as we can"
            this.$nextTick(function() {
                this.focusValue()
            })
        },

        valuedVerb() {
            /* this returns true if the filter's current verb should expose value input(s) */

            // if filter has no "valueless" verbs, then all verbs should expose value inputs
            if (!this.filter.valueless_verbs) {
                return true
            }

            // if filter *does* have valueless verbs, check if "current" verb is valueless
            if (this.filter.valueless_verbs.includes(this.filter.verb)) {
                return false
            }

            // current verb is *not* valueless
            return true
        },

        multiValuedVerb() {
            /* this returns true if the filter's current verb should expose a multi-value input */

            // if filter has no "multi-value" verbs then we safely assume false
            if (!this.filter.multiple_value_verbs) {
                return false
            }

            // if filter *does* have multi-value verbs, see if "current" is one
            if (this.filter.multiple_value_verbs.includes(this.filter.verb)) {
                return true
            }

            // current verb is not multi-value
            return false
        },

        focusValue: function() {
            this.$refs.valueInput.focus()
            // this.$refs.valueInput.select()
        }
    }
}

Vue.component('grid-filter', GridFilter)
