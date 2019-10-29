"use strict"
var DBdata = null;

function initDataTable(json){
    let table = $('#table').DataTable({
        lengthMenu: [ [10, 25, 50, 100, -1], [10, 25, 50, 100, "All"] ],
        data:json['data'],
        columns:json['columns'],
        rowID:'ID',
        colReorder: true,
        scrollX:false,
        paging:true,
        columnDefs: [ {
            orderable: false,
            className: 'select-checkbox',
            targets:   0
        } ],
        select: {
            style:    'multi',
            selector: 'td:first-child'
        },
    });
}

function initColumnsFilter(json){
    let selected = [];
    let hiddenColumns = ['DT_RowId', 'Select']
    json['columns'] = json['columns'].filter((value) => !hiddenColumns.includes(value.title))
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
        let iFactor = stripHTML(factor).split('+');
        for (const readyFactor of iFactor) {
            factors.push(readyFactor.trim());
        }
    }
    factors = new Set(factors);
    let collator = new Intl.Collator(undefined, {numeric: true, sensitivity: 'base'});
    factors = Array.from(factors).sort(collator.compare)

    for (const factor of factors) {
        let options = "<option " + "value='" + stripHTML(factor) + "'>" + factor + "</option>";
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

function stripHTML(html)
{
   let tmp = document.createElement("DIV");
   tmp.innerHTML = html;
   return tmp.textContent || tmp.innerText || "";
}

function initInteractionFilter(json) {
    let interaction = [];
    let interaction_raw = json["data"].map(x => x['Interaction']);
    for (const type of interaction_raw) {
        if(type){
            interaction.push(type.trim());
        }
    }
    interaction = new Set(interaction);
    interaction = Array.from(interaction).sort()

    for (const type of interaction) {
        let options = "<option " + "value='" + stripHTML(type) + "'>" + type + "</option>";
        $("#interactionFilter").append(options);
    }

    $("#interactionFilter").selectpicker('refresh');
}

function initEstimationMethodFilter(json) {
    let estimationMethod = [];
    let estimationMethod_raw = json["data"].map(x => x['Estimation method']);
    for (const type of estimationMethod_raw) {
        if(type){
            estimationMethod.push(type.trim());
        }
    }
    estimationMethod = new Set(estimationMethod);
    estimationMethod = Array.from(estimationMethod).sort()

    for (const type of estimationMethod) {
        let options = "<option " + "value='" + type + "'>" + type + "</option>";
        $("#estimationMethodFilter").append(options);
    }

    $("#estimationMethodFilter").selectpicker('refresh');
}

function getSelectedIDsToForm(){
    let data = $('#table').DataTable().rows( {selected:true} ).data().pluck('DT_RowId').toArray();
    document.getElementById("formIds").value = data
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
            initInteractionFilter(json);
            initEstimationMethodFilter(json);

        },
        complete: function(){
            KTApp.unblockPage();

            $('#columnFilter').on('change', function (){
                let selected = [];
                selected = $('#columnFilter').val()
                //Make select always visible
                selected.push('Select');
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
                            .search(selected.join('|'), true, false)
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
                            .search(selected.join('|'), true, false)
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
                            .search(selected.join('|'), true, false)
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
                            .search(selected.join('|'), true, false)
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
                            .search(selected.join('|'), true, false)
                            .draw();
                    }
                } );
            } );

                $("#table").DataTable().column('Interaction:name').every( function () {
                var that = this;
            
                $('#interactionFilter').on('change', function (){
                    let selected = [];
                    selected = $('#interactionFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search(selected.join('|'), true, false)
                            .draw();
                    }
                } );
            } );
                $("#table").DataTable().column('Estimation method:name').every( function () {
                var that = this;
            
                $('#estimationMethodFilter').on('change', function (){
                    let selected = [];
                    selected = $('#estimationMethodFilter').val()
                    if ( that.search() !== selected ) {
                        that
                            .search(selected.join('|'), true, false)
                            .draw();
                    }
                } );
            } );

        },
        dataType: "json"
    } );

    $('#table').on( 'select.dt deselect.dt', function ( e, dt, type, indexes ) {
        if(type === 'row'){
            let data = $('#table').DataTable().rows( {selected:true} ).data().count()
            $('#compareBtn').toggleClass('disabled', data < 2)        
        } 
    });

    $("#compareForm").submit(function() {
        getSelectedIDsToForm()
      });

})