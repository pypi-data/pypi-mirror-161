## -*- coding: utf-8; -*-

<%def name="feedback_dialog()">
  <script type="text/x-template" id="feedback-template">
    <div>

      <div class="level-item">
        <b-button type="is-primary"
                  @click="showFeedback()"
                  icon-pack="fas"
                  icon-left="fas fa-comment">
          Feedback
        </b-button>
      </div>

      <b-modal has-modal-card
               :active.sync="showDialog">
        <div class="modal-card">

          <header class="modal-card-head">
            <p class="modal-card-title">User Feedback</p>
          </header>

          <section class="modal-card-body">
            <p>
              Questions, suggestions, comments, complaints, etc.
              <span class="red">regarding this website</span> are
              welcome and may be submitted below.
            </p>

            <b-field label="User Name">
              <b-input v-model="userName"
                       % if request.user:
                       disabled
                       % endif
                       >
              </b-input>
            </b-field>

            <b-field label="Referring URL">
              <b-input
                 ## :value="referrer"
                 v-model="referrer"
                 disabled="true">
              </b-input>
            </b-field>

            <b-field label="Message">
              <b-input type="textarea"
                       v-model="message"
                       ref="textarea">
              </b-input>
            </b-field>

          </section>

          <footer class="modal-card-foot">
            <b-button @click="showDialog = false">
              Cancel
            </b-button>
            <once-button type="is-primary"
                         @click="sendFeedback()"
                         :disabled="!message.trim()"
                         text="Send Message">
            </once-button>
          </footer>
        </div>
      </b-modal>

    </div>
  </script>

  <script type="text/javascript">

    FeedbackFormData.csrftoken = ${json.dumps(request.session.get_csrf_token() or request.session.new_csrf_token())|n}
    FeedbackFormData.referrer = location.href

    % if request.user:
    FeedbackFormData.userUUID = ${json.dumps(request.user.uuid)|n}
    FeedbackFormData.userName = ${json.dumps(six.text_type(request.user))|n}
    % endif

    FeedbackForm.data = function() { return FeedbackFormData }

    Vue.component('feedback-form', FeedbackForm)

  </script>
</%def>
