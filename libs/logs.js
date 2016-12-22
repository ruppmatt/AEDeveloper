require(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
    'dojo/domReady!',
  ], function(dom, domConst, xhr, ready){

    /*
    This function will generate our table from the GET request we received.
    The fields are non-log elements retrieved
    The files are fields that are used to generate the URLs to retrieve
    particular log entries.
    */
    function generateTable(results){
      var fields = ['id','date','method','email', 'comment']
      var files = ['log','events','messages','error']

      //Generate the table header
      var header = '<th>' + fields.concat(files).join('</th><th>') + '<th>'
      domConst.place('<tr>' + header + '</tr>', 'logtable');

      //Generate the individual rows from our returned results
      if (typeof results !== 'undefined'){
        for (r of results){
          var row = '';
          for (f of fields){
            r_f = r[f]
            console.log(typeof(r_f) == 'undefined')
            if (typeof(r_f) === 'undefined'){
              r_f = ''
            }
            row = row + '<td>' + r_f + '</td>'
          }
          for (f of files){
            row = row + '<td>';
            row = row + '<a target="_blank" href=http://localhost:5000/log/' + r.id + '/' + f +'>&#x2630;' + '</a>';
            row = row + '</td>';
          }
          domConst.place('<tr>' + row + '</tr>', 'logtable')
        }
      }
    }

    //Try to be RESTful and use GET
    xhr.get(  //get is a helper function to xhr, a more generic class
      'http://localhost:5000/getlogs',  //URL parameter
        {  //Data and halding parameter
        }
    ).then(function(response){ //Promise format; received data from request (first param of then)
        jresponse = JSON.parse(response)
        generateTable(jresponse.results);
      }, function(err){ //Error handling (second param of then)
        domConst.place('<p>Error: <code>' + JSON.stringify(err.response) + '</code></p>', 'status');
      }
    ); // End then

  }
);
