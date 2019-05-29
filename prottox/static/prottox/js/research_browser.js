$(document).ready(function () {

    var ids = JSON.parse(document.getElementById('IDs').textContent);
    var db = JSON.parse(document.getElementById('DB').textContent);

    var API_ADDR = '/api/researchbrowser?ids='+ids+'&db='+db;
    $.ajax( {
        "url": API_ADDR,
        "success": function ( json ) {
            $('#table').dataTable( json );
        },
        "dataType": "json"
    } );
})