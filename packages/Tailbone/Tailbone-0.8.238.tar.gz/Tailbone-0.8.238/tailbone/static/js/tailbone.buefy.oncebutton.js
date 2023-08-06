
const OnceButton = {

    template: `
        <b-button :type="type"
                  :native-type="nativeType"
                  :tag="tag"
                  :href="href"
                  :title="title"
                  :disabled="buttonDisabled"
                  @click="clicked"
                  icon-pack="fas"
                  :icon-left="iconLeft">
          {{ buttonText }}
        </b-button>
        `,

    props: {
        type: String,
        nativeType: String,
        tag: String,
        href: String,
        text: String,
        title: String,
        iconLeft: String,
        working: String,
        workingText: String,
        disabled: Boolean
    },

    data() {
        return {
            currentText: null,
            currentDisabled: null,
        }
    },

    computed: {
        buttonText: function() {
            return this.currentText || this.text
        },
        buttonDisabled: function() {
            if (this.currentDisabled !== null) {
                return this.currentDisabled
            }
            return this.disabled
        },
    },

    methods: {

        clicked(event) {
            this.currentDisabled = true
            if (this.workingText) {
                this.currentText = this.workingText
            } else if (this.working) {
                this.currentText = this.working + ", please wait..."
            } else {
                this.currentText = "Working, please wait..."
            }
            this.$nextTick(function() {
                this.$emit('click', event)
            })
        }
    }

}

Vue.component('once-button', OnceButton)
