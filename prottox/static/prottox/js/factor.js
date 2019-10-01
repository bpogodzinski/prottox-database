FACTOR_ROOT_URL = "/api/factortaxonomy/";

function initFactorTree() {
  $("#tree")
    .jstree({
      core: {
        check_callback: true,
        data: {
          url: function(node) {
            return FACTOR_ROOT_URL;
          },
          data: function(node) {
            return;
          }
        }
      },
      checkbox: {
        whole_node: false,
        tie_selection: false
      },
      types: {
        default: {
          icon: "fas fa-folder"
        }
      },
      search: {
        "case_sensitive":false,
        "show_only_matches":true
      },
      plugins: ["checkbox", "types", "state", "search"]
    })
    .on("open_node.jstree", function(e, data) {
      data.instance.set_icon(data.node, "fas fa-folder-open");
    })
    .on("close_node.jstree", function(e, data) {
      data.instance.set_icon(data.node, "fas fa-folder");
    });
}

// ------------Form submit methods-------------

function prepareCheckedData() {
    let dataEntity = $("#tree").jstree("get_node", 1)["original"]["entity"];
    let selected = "";
    if (dataEntity === "factor") {
      selected = $("#tree").jstree("get_checked", true);
    } else {
      selected = $("#tree").jstree("get_bottom_checked", true);
    }
    let ids = selected.map(x => x["id"]);
    document.getElementById("formIds").value = ids;
    document.getElementById("formEntity").value = dataEntity;
  }
  
  $("#form").submit(function() {
    prepareCheckedData();
  });
  
  // ------------Document ready--------------
  $(document).ready(function() {
  
    $(".search-input").keyup(function () {
      var searchString = $(this).val();
      $('#tree').jstree('search', searchString);
    });
  
    initFactorTree();
  });