function initDataTable(json){
    $('#table').dataTable({
        data:json['data'],
        columns:json['columns'],
        colReorder: true,
        scrollX:false,
        paging:true,
    });

}

$(document).ready(function () {

    var ids = JSON.parse(document.getElementById('IDs').textContent);
    var db = JSON.parse(document.getElementById('DB').textContent);
    var API_ADDR = '/api/researchbrowser?ids='+ids+'&db='+db;

    $.ajax( {
        url: API_ADDR,
        success: function ( json ) {
            initDataTable(json);
        },
        dataType: "json"
    } );
})