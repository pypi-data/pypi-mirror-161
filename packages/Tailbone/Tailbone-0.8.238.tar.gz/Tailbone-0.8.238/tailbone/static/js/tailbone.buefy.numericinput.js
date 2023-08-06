
const NumericInput = {
    template: [
        '<b-input',
        ':name="name"',
        ':value="value"',
        'ref="input"',
        ':placeholder="placeholder"',
        ':size="size"',
        ':icon-pack="iconPack"',
        ':icon="icon"',
        ':disabled="disabled"',
        '@focus="notifyFocus"',
        '@blur="notifyBlur"',
        '@keydown.native="keyDown"',
        '@input="valueChanged"',
        '>',
        '</b-input>'
    ].join(' '),

    props: {
        name: String,
        value: [Number, String],
        placeholder: String,
        iconPack: String,
        icon: String,
        size: String,
        disabled: Boolean,
        allowEnter: Boolean
    },

    methods: {

        focus() {
            this.$refs.input.focus()
        },

        notifyFocus(event) {
            this.$emit('focus', event)
        },

        notifyBlur(event) {
            this.$emit('blur', event)
        },

        keyDown(event) {
            // by default we only allow numeric keys, and general navigation
            // keys, but we might also allow Enter key
            if (!key_modifies(event) && !key_allowed(event)) {
                if (!this.allowEnter || event.which != 13) {
                    event.preventDefault()
                }
            }
        },

        select() {
            this.$el.children[0].select()
        },

        valueChanged(value) {
            this.$emit('input', value)
        }

    }
}

Vue.component('numeric-input', NumericInput)
