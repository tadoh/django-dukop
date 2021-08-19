$(function () {
    $(".close").click(function() {
    console.log("hej");
        $(this).closest(".card-messages").hide("fast");
    });
});
