$(document).ready(function() {
    $('.formset-add-link').click(function() {
        $(this).parents(".formset--element").first().next().show('fast');
    });
    $('.formset-remove-link').click(function() {
        $(this).parents(".formset--element").first().hide('fast');
    });
});


// https://stackoverflow.com/a/54574537/405682
var isSubmitting = false;

$(document).ready(function () {
    $('.event__form').submit(function(){
        isSubmitting = true;
    });

    $('form').data('initial-state', $('.event__form').serialize());

    $(window).on('beforeunload', function() {
        if (!isSubmitting && $('form').serialize() != $('form').data('initial-state')){
            return 'You have unsaved changes which will not be saved.';
        }
    });
});
