## -*- coding: utf-8; -*-
<%inherit file="/progress.mako" />

<%def name="update_progress_func()">
  <script type="text/javascript">

      function update_progress() {
          $.ajax({
              url: '${url('upgrades.execute_progress', uuid=instance.uuid)}',
              success: function(data) {
                  if (data.error) {
                      location.href = '${cancel_url}';
                  } else {

                      if (data.stdout) {
                          var stdout = $('.stdout');
                          var height = $(window).height() - stdout.offset().top - 50;
                          stdout.height(height);
                          stdout.append(data.stdout);
                          stdout.animate({scrollTop: stdout.get(0).scrollHeight - height}, 250);
                      }

                      if (data.complete || data.maximum) {
                          $('#message').html(data.message);
                          $('#total').html('('+data.maximum_display+' total)');
                          $('#cancel button').show();
                          if (data.complete) {
                              stillInProgress = false;
                              $('#cancel button').hide();
                              $('#total').html('done!');
                              $('#complete').css('width', '100%');
                              $('#remaining').hide();
                              $('#percentage').html('100 %');
                              location.href = data.success_url;
                          } else {
                              var width = parseInt(data.value) / parseInt(data.maximum);
                              width = Math.round(100 * width);
                              if (width) {
                                  $('#complete').css('width', width+'%');
                                  $('#percentage').html(width+' %');
                              } else {
                                  $('#complete').css('width', '0.01%');
                                  $('#percentage').html('0 %');
                              }
                              $('#remaining').css('width', 'auto');
                          }
                      }

                      if (stillInProgress) {
                          // fetch progress data again, in one second from now
                          setTimeout(function() {
                              update_progress();
                          }, 1000);
                      }
                  }
              }
          });
      }
  </script>
</%def>

<%def name="extra_styles()">
  ${parent.extra_styles()}
  <style type="text/css">
    #wrapper {
        top: 6em;
    }
    .stdout {
        border: 1px solid Black;
        height: 500px;
        margin-left: 4.5%;
        overflow: auto;
        padding: 4px;
        position: absolute;
        top: 10em;
        white-space: nowrap;
        width: 90%;
    }
  </style>
</%def>

<%def name="after_progress()">
  <div class="stdout"></div>
</%def>

${parent.body()}
