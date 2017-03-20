define(
  [
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/request/xhr',
  ], function(dom, domConst, xhr, ready){

    function get_report_metadata(callback, error){

      //Try to be RESTful and use GET
      xhr.get(  //get is a helper function to xhr, a more generic class
        'http://localhost:5000/report/metadata',  //URL parameter
          {  //Data and halding parameter
            handleAs:'json',
            headers:{
              'X-Requested-With':null
            },
            withCredentials:true
          }
      ).then(callback, error); //Promise format; received data from request (first param of then)
    }

    return {get_report_metadata:get_report_metadata};

});
