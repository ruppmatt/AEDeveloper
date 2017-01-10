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

      xhr.post(  //Post is a helper function to xhr, a more generic class
        'http://localhost:5000/receive',  //URL parameter
          {  //Data and halding parameter
            handleAs:'json',
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
            }
          }
      ).then(function(received){ //Promise format; received data from request (first param of then)
          domConst.place('<p>Data received: <code>' + JSON.stringify(received) + '</code></p>', 'status');
        }, function(err){ //Error handling (second param of then)
          domConst.place('<p>Error: <code>' + JSON.stringify(err) + '</code></p>', 'status');
        }
      ); // End then
    }); // End on's function and on statement
  } //End require function body
); // End require
