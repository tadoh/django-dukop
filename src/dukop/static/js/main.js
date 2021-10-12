$("input.share-text-input").focus(function() {
   $(this).select();
   $(this).attr("readonly", true);
});

function copy() {
   var copyText = document.querySelector("input.share-text-input");
   copyText.select();
   document.execCommand("copy");
 }
 
if (document.querySelector(".js-copy")) {
   document.querySelector(".js-copy").addEventListener("click", copy);
}