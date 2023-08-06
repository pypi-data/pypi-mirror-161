## -*- coding: utf-8; -*-

<%def name="declare_formposter_mixin()">
  <script type="text/javascript">

    let FormPosterMixin = {
        methods: {

            submitForm(action, params, success, failure) {

                let csrftoken = ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n}

                let headers = {
                    '${csrf_header_name}': csrftoken,
                }

                this.$http.post(action, params, {headers: headers}).then(response => {

                    if (response.data.ok) {
                        success(response)

                    } else {
                        this.$buefy.toast.open({
                            message: "Submit failed:  " + (response.data.error ||
                                                           "(unknown error)"),
                            type: 'is-danger',
                            duration: 4000, // 4 seconds
                        })
                        if (failure) {
                            failure(response)
                        }
                    }

                }, response => {
                    this.$buefy.toast.open({
                        message: "Submit failed!  (unknown server error)",
                        type: 'is-danger',
                        duration: 4000, // 4 seconds
                    })
                    if (failure) {
                        failure(response)
                    }
                })
            },
        },
    }

  </script>
</%def>
