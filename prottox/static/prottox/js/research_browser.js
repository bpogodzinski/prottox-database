"use strict"
var DBdata = null;

function initDataTable(json){
    $('#table').DataTable({
        data:json['data'],
        columns:json['columns'],
        colReorder: true,
        scrollX:false,
        paging:true,
    });

}

function initColumnsFilter(json){
    let selected = [];

    for (const column of json['columns']) {
        if(column.visible === true){
            selected.push(column.title)
        }
        var options = "<option " + "value='" + column.title + "'>" + column.title + "</option>";
        $("#columnFilter").append(options);
    }

    $("#columnFilter").selectpicker('val', selected);
    $("#columnFilter").selectpicker('refresh');
}

function initFactorFilter(json) {
    let factors = [];
    let factors_raw = json["data"].map(x => x.Factor);
    for (const factor of factors_raw) {
        let iFactor = factor.split('+');
        for (const readyFactor of iFactor) {
            factors.push(readyFactor.trim());
        }
    }
    factors = new Set(factors);
    let collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
    factors = Array.from(factors).sort(collator.compare)

    for (const factor of factors) {
        let options = "<option " + "value='" + factor + "'>" + factor + "</option>";
        $("#factorFilter").append(options);
    }

    $("#factorFilter").selectpicker('refresh');
}
  


$(document).ready(function () {

    var ids = JSON.parse(document.getElementById('IDs').textContent);
    var db = JSON.parse(document.getElementById('DB').textContent);
    var API_ADDR = '/api/researchbrowser?ids='+ids+'&db='+db;
    
    $.ajax( {
        url: API_ADDR,
        beforeSend: function(){
            KTApp.blockPage({
                type: 'v2',
                state: 'success',
                size: 'lg',
                message: 'Please wait...'
            });
        },
        success: function ( json ) {
            DBdata = json;
            initDataTable(json);
            initColumnsFilter(json);
            initFactorFilter(json);

        },
        complete: function(){
            KTApp.unblockPage();

            $('#columnFilter').on('change', function (){
                let selected = [];
                selected = $('#columnFilter').val()
                $("#table").DataTable().columns().visible(false);
                for (const columnName of selected) {
                    let column = $("#table").DataTable().column(columnName+':name');
                    column.visible(true);
                }
              });
            

              $("#table").DataTable().column('Factor:name').every( function () {
                var that = this;
         
                $('#factorFilter').on('change', function (){
                    let selected = [];
                    selected = $('#factorFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search( selected.join(' ') )
                            .draw();
                    }
                } );
            } );        
        },
        dataType: "json"
    } );
})