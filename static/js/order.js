$(document).ready(function(){

    $(".order-detail").click(function(e) {
        var endpoint = $(this).attr("data-url");
         console.log(endpoint)
         $.ajax({
             method: 'GET',
             url: endpoint,
             success: function(data) {
                 console.log(data);
                //  var target_span = $(".order_detail_id").text();
                 $(".order_detail_id").text(data.id);
                 var total_span = $(".order_total_amount").text();
                 $(".order_total_amount").text(data.total);
                 console.log(total_span);
                 $('#cancel_order').attr("href", data.cancel);
                 $(".total_items_count").text(data.items)
             },
             error: function(error_data) {
                 console.log(error_data)
             }
         })
    })
})