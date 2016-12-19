require(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
    'dojo/on',
    'dojo/domReady!'
  ], function(dom, domConst, xhr, on) {

    //JSON data to send
    var data_to_send = { key1:'value1', key2:{key3:'value3'} };

    //Everything happens when we click a button
    on(dom.byId('send_button'), 'click', function(){

      domConst.place('<p>Button pressed; send message</p>', 'status');

      xhr.post(  //Post is a helper function to xhr, a more generic class
        'http://localhost:5000/receive',  //URL parameter
          {  //Data and halding parameter
            data:JSON.stringify(data_to_send)
          }
      ).then(function(received){ //Promise format; received data from request (first param of then)
          domConst.place('<p>Data received: <code>' + received + '</code></p>', 'status');
        }, function(err){ //Error handling (second param of then)
          domConst.place('<p>Error: <code>' + err + '</code></p>', 'status');
        }
      ); // End then
    }); // End on's function and on statement
  } //End require function body
); // End require
