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

function initTargetSpeciesFilter(json) {
    let targetSpecies = [];
    let targetSpecies_raw = json["data"].map(x => x['Target species']);
    for (const species of targetSpecies_raw) {
        targetSpecies.push(species.trim());
    }
    targetSpecies = new Set(targetSpecies);
    targetSpecies = Array.from(targetSpecies).sort()

    for (const species of targetSpecies) {
        let options = "<option " + "value='" + species + "'>" + species + "</option>";
        $("#targetSpeciesFilter").append(options);
    }

    $("#targetSpeciesFilter").selectpicker('refresh');
}

function initLarvaeStageFilter(json) {
    let larvaeStage = [];
    let larvaeStage_raw = json["data"].map(x => x['Target larvae stage']);
    for (const stage of larvaeStage_raw) {
        larvaeStage.push(stage.trim());
    }
    larvaeStage = new Set(larvaeStage);
    larvaeStage = Array.from(larvaeStage).sort()

    for (const stage of larvaeStage) {
        let options = "<option " + "value='" + stage + "'>" + stage + "</option>";
        $("#targetLarvaeStageFilter").append(options);
    }

    $("#targetLarvaeStageFilter").selectpicker('refresh');
}

function initTargetFactorResistanceFilter(json) {
    let factorResistance = [];
    let factorResistance_raw = json["data"].map(x => x['Target factor resistance']);
    for (const factor of factorResistance_raw) {
        if (factor) {
            let iFactor = factor.split(',');
            for (const readyFactor of iFactor) {
                factorResistance.push(readyFactor.trim());
            }
        }
    }
    factorResistance = new Set(factorResistance);
    factorResistance = Array.from(factorResistance).sort()

    for (const factor of factorResistance) {
        let options = "<option " + "value='" + factor + "'>" + factor + "</option>";
        $("#targetFactorResistanceFilter").append(options);
    }

    $("#targetFactorResistanceFilter").selectpicker('refresh');
}

function initToxinDistributionFilter(json) {
    let toxinDistrib = [];
    let toxin_raw = json["data"].map(x => x['Toxin distribution']);
    for (const toxin of toxin_raw) {
        toxinDistrib.push(toxin.trim());
    }
    toxinDistrib = new Set(toxinDistrib);
    toxinDistrib = Array.from(toxinDistrib).sort()

    for (const iToxin of toxinDistrib) {
        let options = "<option " + "value='" + iToxin + "'>" + iToxin + "</option>";
        $("#toxinDistributionFilter").append(options);
    }

    $("#toxinDistributionFilter").selectpicker('refresh');
}

function initBioassayTypeFilter(json) {
    let bioassayType = [];
    let bioassayType_raw = json["data"].map(x => x['Bioassay type']);
    for (const type of bioassayType_raw) {
        bioassayType.push(type.trim());
    }
    bioassayType = new Set(bioassayType);
    bioassayType = Array.from(bioassayType).sort()

    for (const type of bioassayType) {
        let options = "<option " + "value='" + type + "'>" + type + "</option>";
        $("#bioassayTypeFilter").append(options);
    }

    $("#bioassayTypeFilter").selectpicker('refresh');
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
            initTargetSpeciesFilter(json);
            initLarvaeStageFilter(json);
            initTargetFactorResistanceFilter(json);
            initToxinDistributionFilter(json);
            initBioassayTypeFilter(json);

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
                    
              $("#table").DataTable().column('Target species:name').every( function () {
                var that = this;
         
                $('#targetSpeciesFilter').on('change', function (){
                    let selected = [];
                    selected = $('#targetSpeciesFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search( selected.join(' ') )
                            .draw();
                    }
                } );
            } );

              $("#table").DataTable().column('Target larvae stage:name').every( function () {
                var that = this;
         
                $('#targetLarvaeStageFilter').on('change', function (){
                    let selected = [];
                    selected = $('#targetLarvaeStageFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search( selected.join(' ') )
                            .draw();
                    }
                } );
            } );

                $("#table").DataTable().column('Target factor resistance:name').every( function () {
                var that = this;
            
                $('#targetFactorResistanceFilter').on('change', function (){
                    let selected = [];
                    selected = $('#targetFactorResistanceFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search( selected.join(' ') )
                            .draw();
                    }
                } );
            } );
            
                $("#table").DataTable().column('Toxin distribution:name').every( function () {
                var that = this;
            
                $('#toxinDistributionFilter').on('change', function (){
                    let selected = [];
                    selected = $('#toxinDistributionFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search( selected.join(' ') )
                            .draw();
                    }
                } );
            } );

                $("#table").DataTable().column('Bioassay type:name').every( function () {
                var that = this;
            
                $('#bioassayTypeFilter').on('change', function (){
                    let selected = [];
                    selected = $('#bioassayTypeFilter').val()
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