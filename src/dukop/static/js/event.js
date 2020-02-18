$(document).ready(function() {
    $('.timeslot-add-link').click(function() {
        var element_id = $(this).data("toggle");
        $(element_id).show('fast');
    });
    $('.timeslot-remove-link').click(function() {
        var element_id = $(this).data("toggle");
        $(element_id).hide('fast');
    });
});
