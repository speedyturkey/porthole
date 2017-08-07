$( document ).ready(function() {
  $('#edit-general-settings').click(function(){

    if($('#edit-general-settings').text()==='Edit Settings'){
      $('.gen-set-field').prop('disabled', false);
      $('#edit-general-settings').text('Cancel');
    } else {
      location.reload();
    }

    //$('#edit-general-settings').hide();
    //$('.cancel-edit').hide();
  });
  $('.cancel-edit').click(function(){

  });



});
