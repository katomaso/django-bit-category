/**
    A javascript which dynamically creates / deletes Selects according
    to AJAX requests for django-bit-category views.

    Requires jquery (surprise)
**/

$(document).ready(function(){

    function hierarchical_handle_ajax(data, status, xhr) {
        var caller = $("#" + data.caller);
        var re = new RegExp(/([a-zA-Z_]+)(\d)/g);  // for id/name change
        // remove all "deeper" selects
        var i = data.level;
        var deeper_id = data.caller.replace(re, "$1" + i);
        while($("#" + deeper_id).length > 0) {
            $("#" + deeper_id).remove();
            i += 1;
            deeper_id = data.caller.replace(re, "$1" + i);
        }
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
                        .text("---------------")
                     );
        $.each(data.items, function(i, item) {
            select.append($('<option></option>')
                .attr("value", item[0])
                .text(item[1]));
        });
        caller.parent().append(select);
    }


    $(".hierarchical_widget").on("change", function(event) {
        var selected_id = $(this).children("option:selected").val();
        var url = $(this).attr("data:url");
        $.get(url, {"id": selected_id, "caller": $(this).attr("id")},
              hierarchical_handle_ajax, "json"
        ).fail(function() {console.log("Hierarchical request did not succeeded");});
    });
});