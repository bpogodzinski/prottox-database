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
        beforeSend: function(){
            KTApp.block('#research_table', {
                type: 'v2',
                state: 'success',
                size: 'lg',
                message: 'Please wait...'
            });
        },
        success: function ( json ) {
            initDataTable(json);
        },
        complete: function(){
            KTApp.unblock('#research_table');
        },
        dataType: "json"
    } );
})