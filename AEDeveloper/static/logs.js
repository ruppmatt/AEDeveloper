define(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
  ], function(dom, domConst, xhr, ready){

    function all_report_metadata(callback, error){

      var test = {foo:'bar', baz:['cat', 'bat', 'rat']}
      //Try to be RESTful and use GET
      xhr.get(  //get is a helper function to xhr, a more generic class
        'http://localhost:5000/getlogs',  //URL parameter
          {  //Data and halding parameter
            handleAs:'json',
            headers:{
              'X-Requested-With':null
            }
          }
      ).then(callback(respones), error(err)); //Promise format; received data from request (first param of then)
  }

);
