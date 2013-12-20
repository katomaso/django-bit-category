/**
    A javascript which dynamically creates / deletes Selects according
    to AJAX requests for django-bit-category views.

    Requires jquery (surprise)
**/

$(document).ready(function(){

    function hierarchical_handle_ajax(data, status, xhr) {
        var caller = $("#" + data.caller);
        var re = new RegExp(/([a-zA-Z_]+)(\d+)/g);  // for id/name change
        // remove all "deeper" selects
        hierarchical_clean_successors(caller);
        // if there are no new data, quit
        if (data.items.length === 0) return;
        // clone select and exchange it's items
        select = caller.clone(true);  // copy with data and events
        select.children().remove("option"); // clean children
        select.attr("id", caller.attr("id").replace(re, "$1" + data.level)); // change id
        select.attr("name", caller.attr("name").replace(re, "$1" + data.level)); // change name
        // append first - empty option
        select.append($('<option></option>')
                        .attr("value", null)
                        .text("----------------")
                     );
        $.each(data.items, function(i, item) {
            select.append($('<option></option>')
                .attr("value", item[0])
                .text(item[1]));
        });
        caller.parent().append(select);
    }

    function hierarchical_bad_request(caller) {
        return function (data, status, xhr) {
            hierarchical_clean_successors(caller);
        };
    }

    function hierarchical_clean_successors(caller) {
        var caller_id = caller.attr("id");
        var re = new RegExp(/([a-zA-Z_]+)(\d+)/g);  // for id/name change
        var captures = re.exec(caller_id);
        var level =  parseInt(captures[2], 10) + 1;
        var deeper_id = caller_id.replace(re, "$1" + level.toString());
        while($("#" + deeper_id).length > 0) {
            $("#" + deeper_id).remove();
            level += 1;
            deeper_id = caller_id.replace(re, "$1" + level.toString());
        }
    }

    $(".hierarchical_widget").on("change", function(event) {
        var selected_id = $(this).children("option:selected").val();
        if (selected_id === null) {
            hierarchical_clean_successors($(this));
            return false;
        }
        var url = $(this).attr("data:url");
        $.ajax(url, {
            "type": "GET",
            "dataType": "json",
            "data": {"id": selected_id,
                     "caller": $(this).attr("id")},
            "success": hierarchical_handle_ajax,
            "error": hierarchical_bad_request($(this))
            }
        );
    });
});
