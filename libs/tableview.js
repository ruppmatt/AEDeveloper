require(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
    'dojo/domReady!',
  ], function(dom, domConst, xhr, ready){

    function generate_table(response){
      dom.byId('logtable').place('<tr><th>log_id</th><th>date</th><th>comments</th></tr>');
      if (defined(response.results)){
      }
    }
    
    //Try to be RESTful and use GET
    xhr.get(  //Post is a helper function to xhr, a more generic class
      'http://localhost:5000/tableview',  //URL parameter
        {  //Data and halding parameter
        }
    ).then(function(response){ //Promise format; received data from request (first param of then)
        generateTable(response);
      }, function(err){ //Error handling (second param of then)
        domConst.place('<p>Error: <code>' + JSON.stringify(err) + '</code></p>', 'status');
      }
    ); // End then

  }
);
