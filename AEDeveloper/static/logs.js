define(
  [
    'jquery',
    'dojo/dom',
    'dojo/dom-construct',
    'dojo/html',
    'dojo/request/xhr',
  ], function($, dom, domConst, html, xhr, ready){

    function getReportsMetadata(callback, error){

      //Try to be RESTful and use GET
      xhr.get(  //get is a helper function to xhr, a more generic class
        'http://localhost:5000/report/all',  //URL parameter
          {  //Data and halding parameter
            handleAs:'json',
            headers:{
              'X-Requested-With':null
            },
            withCredentials:true
          }
      ).then(callback, error); //Promise format; received data from request (first param of then)
    }

    //Get jquery and json view (which depends on it) seutp
    $.getScript('/static/jquery.jsonview.js');


    function generateReportElement(report){
      var report_div = domConst.create('div', {class:'report'});
      var report_header = domConst.create('div', {class:'header'}, report_div);
      var report_body = domConst.create('div', {class:'body'}, report_div);

      domConst.create('div', {class:'id', textContent:report.id}, report_header);
      domConst.create('div', {class:'date', textContent:report.date}, report_header);
      domConst.create('div', {class:'triggered', textContent:report.triggered}, report_header);
      domConst.create('div', {class:'email', textContent:report.email}, report_header);

      var report_metadata = domConst.create('table', {class:'metadta_table'}, report_body);

      ['id', 'date', 'triggered', 'email', 'comment', 'version',  'userInfo', 'vars', 'screenSize', 'error']
      for (f of ['comment', 'version', 'userAgent', 'userInfo', 'vars', 'screenSize', 'error']){
        var r = domConst.create('tr', {}, report_metadata);
        domConst.create('td', {class:'fieldname', textContent:f}, r);
        if (f !== 'vars'){
          domConst.create('td', {textContent:report[f]},r);
        } else {
          var d = domConst.create('td', {}, r);
          $(d).JSONView(report['vars'], {collapsed:true, recursiveCollapser:true, nl2br:true});
        }
        domConst.place(r,report_metadata);
      }
      var r = domConst.create('tr', {}, report_metadata);
      domConst.create('td', {class:'fieldname', textContent:'logs'}, r)
      var log_cell = domConst.create('td', {}, r);
      var log_table = domConst.create('table', {class:'log_table'}, log_cell);
      for (l of report['logs']){
        var log_entry = domConst.create('tr', {class:'entry'}, log_table);
        domConst.create('td', {class:'log_name', textContent:l}, log_entry);
        for (mode of ['raw', 'html']){
          var log_uri = window.location.pathname + '/' + report['id'] + '/' + l + '/' + mode;
          var e = domConst.create('td', {class:'log_mode'}, log_entry);
          if (mode == 'raw'){
            domConst.create('a', {href:log_uri, class:'log_uri', textContent:mode}, e);
          } else {
            e.textContent = mode;
          }
        }
      }
      return report_div
    }

    return {
      getReportsMetadata:getReportsMetadata,
      generateReportElement:generateReportElement
    };

});
