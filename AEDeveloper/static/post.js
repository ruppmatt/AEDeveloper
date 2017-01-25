require(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
    'dojo/on',
    'dojo/domReady!',
    'ipsum'
  ], function(dom, domConst, xhr, on, ready, ipsum) {

    //foo



    //Everything happens when we click a button
    on(dom.byId('send_button'), 'click', function(){

      //Data to send
      var a_log = ipsum.paragraphs(5,true).join('\n\n');
      var a_comment = ipsum.paragraph();
      var a_jserror = ipsum.sentence();
      var a_email = 'foo@bar.baz';
      var a_events = ipsum.paragraphs(5,true).join('\n\n');
      var a_method = 'userTriggered';
      var a_messages = ipsum.paragraphs(5,true).join('\n\n');

      domConst.place('<p>Button pressed; send message</p>', 'status');

      var request = xhr.post(  //Post is a helper function to xhr, a more generic class
        'http://localhost:5000/receive',  //URL parameter
          {  //Data and halding parameter
            data:{
              log:a_log,
              comment:a_comment,
              error:a_jserror,
              email:a_email,
              events:a_events,
              method:a_method,
              messages:a_messages
            },
            headers: {
              'X-Requested-With':null
            },
            timeout:1000
          }
      );

      request.response.then(function(response){ //Promise format; received data from request (first param of then)
          domConst.place('<p><code>' + JSON.stringify(response) + '</code></p>', 'status');
        }, function(err) {
          domConst.place('<p>Err: <code>' + JSON.stringify(err) + '</code></p>', 'status');
        }
      ); // End then


    }); // End on's function and on statement
  } //End require function body
); // End require
