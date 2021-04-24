$("input.share-text-input").focus(function() {
   $(this).select();
   $(this).attr("readonly", true);
});
