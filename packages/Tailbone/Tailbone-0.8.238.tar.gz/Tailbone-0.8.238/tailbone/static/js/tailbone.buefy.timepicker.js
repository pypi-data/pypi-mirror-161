
const TailboneTimepicker = {

    template: [
        '<b-timepicker',
        ':name="name"',
        ':id="id"',
        'editable',
        'placeholder="Click to select ..."',
        'icon-pack="fas"',
        'icon="clock"',
        'hour-format="12"',
        '>',
        '</b-timepicker>'
    ].join(' '),

    props: {
        name: String,
        id: String
    }
}

Vue.component('tailbone-timepicker', TailboneTimepicker)
