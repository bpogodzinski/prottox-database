FACTOR_ROOT_URL = 'api/factortaxonomy/'
TARGET_ROOT_URL = 'api/targettaxonomy/'
// function addChildrenNodes(nodeData) {
//     let selected = nodeData.instance.get_node(nodeData.selected)
//     $.ajax(
//         {
//             url: FACTOR_ROOT_URL,
//             data: {
//                 parent_id: selected.id
//             },
//             success: function (newNodes) {
//                 var index;
//                 for (index = 0; index < newNodes.length; ++index) {
//                     if (!$('#factorTree').jstree(true).get_node(newNodes[index].id)) {
//                         $('#factorTree').jstree('create_node', selected.id, newNodes[index])
//                     }
//                 }
//                 $('#factorTree').jstree('open_node',selected.id)

//             }
//         }
//     )
// }

function initFactorTree(){

    $('#factorTree').jstree({
        core: {
            check_callback: true,
            data: {
                url: function (node) {
                    return FACTOR_ROOT_URL;
                },
                data: function (node) {
                    return;
                }
            }
        },
        checkbox: {
            whole_node: false,
            tie_selection: false,
        },
        plugins: ['checkbox'],
    })
}

function initTargetTree(){

    $('#targetTree').jstree({
        core: {
            check_callback: true,
            data: {
                url: function (node) {
                    return TARGET_ROOT_URL;
                },
                data: function (node) {
                    return;
                }
            }
        },
        checkbox: {
            whole_node: false,
            tie_selection: false,
        },
        plugins: ['checkbox'],
    })
}


// ------------Document ready--------------
$(document).ready(function () {
    initFactorTree()
    initTargetTree()
    
})
