$(document).ready(function() {
    // executes when HTML-Document is loaded and DOM is ready
   console.log("document is ready");
     
   
     $( ".card" ).hover(
     function() {
       $(this).addClass('shadow-lg moveUp').css('cursor', 'pointer'); 
     }, function() {
       $(this).removeClass('shadow-lg moveUp');
     }
   );
     
   // document ready  
   });
   
   
   
