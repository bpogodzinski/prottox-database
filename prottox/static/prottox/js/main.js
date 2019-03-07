ROOT_URL = 'api/taxonomy/'

function addChildrenNodes(nodeData) {
    let selected = nodeData.instance.get_node(nodeData.selected)
    $.ajax(
        {
            url: ROOT_URL,
            data: {
                parent_id: selected.id
            },
            success: function (newNodes) {
                var index;
                for (index = 0; index < newNodes.length; ++index) {
                    if (!$('#tree').jstree(true).get_node(newNodes[index].id)) {
                        $('#tree').jstree('create_node', selected.id, newNodes[index])
                    }
                }
                $('#tree').jstree('open_node',selected.id)

            }
        }
    )
}

// ------------Document ready--------------
$(document).ready(function () {
    $('#tree').jstree({
        core: {
            check_callback: true,
            data: {
                url: function (node) {
                    return ROOT_URL;
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
    })//.on('select_node.jstree', (e, data) => addChildrenNodes(data))
})
