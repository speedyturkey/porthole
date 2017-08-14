$( document ).ready(function() {
  $('#edit-general-settings').click(function(){

    if($('#edit-general-settings').text()==='Edit Settings'){
      $('.gen-set-field').prop('disabled', false);
      $('#edit-general-settings').text('Cancel');
      $('#save-general-settings').show();
    } else {
      location.reload();
    }
  });

  $('#save-general-settings').click(function(){
    $('#config_submit').click();
  });

  $('#add-connection').click(function(){
    if($('#add-connection').text()==='Add Connection'){
      $('#connection-form').show();
      $('#add-connection').text('Cancel');
    } else {
      location.reload();
    }
  });

  $('.edit-connection').click(function(){
    $('#connection-form').show();
    $('#add-connection').text('Cancel');
    var connection = this.id.split('-')[1];
    console.log(allConfigOptions);
    $('#connection_name').val(connection);
    $('#rdbms').val(allConfigOptions[connection]['rdbms']);
    $('#connection_host').val(allConfigOptions[connection]['host']);
    $('#connection_port').val(allConfigOptions[connection]['port']);
    $('#connection_user').val(allConfigOptions[connection]['user']);
    // $('#connection_password').val(allConfigOptions[connection]['password']);
    $('#schema').val(allConfigOptions[connection]['schema']);
  });

  $('.delete-connection').click(function(){
    var connection = this.id.split('-')[1];
    $('#connection_name').val(connection);
    $('#delete_connection').val('True');
    $('#connection_submit').click();
  });



});
