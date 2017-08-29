'use strict';
$( document ).ready(function() {

// Settings Page ---------------------------------------------------------------
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

  $('.test-connection').click(function(){
    var connection = this.id.split('-')[1];
    console.log(connection);
    var testResultId = 'test-result-' + connection;
    $.get($SCRIPT_ROOT + '/api/test_connection/' + encodeURI(connection), function(result){
      $('#'+testResultId).text(result);
    });
  });

//Query Page -------------------------------------------------------------------
  $('#connection-selection').change(function(){
    var connection = '';
    connection = $('#connection-selection').val();
    $('#table-column-results').hide();
    $('#connection-message').text('');
    $('query-connect').text('Connect');
    if(connection != 'None Selected'){
      $('#connect-btn-row').show();
    } else {
      $('#connect-btn-row').hide();
    }
  })

  $('#query-connect').click(function(){
    $('#connection-message').text('Connecting...');
    var connection = $('#connection-selection').val();
    $('#connection-columns').text('');
    $('#connection-tables').text('');
    $.get($SCRIPT_ROOT + '/api/schema_info/' + encodeURI(connection), function(result){
      if(Array.isArray(result)){    //checks to ensure connection was successful
        var schemas = [];
        var tables = [];
        schemas = getSchemas(result);     //function to get array of schemas in connection
        $('#connection-message').text('Connected');
        $('#query-connect').text('Refresh Connection');
        $('#table-column-results').show();
        for (var schema of schemas){      //loop through each schema
          $('#connection-tables').append(
            '<div class="row schema-name" id="schema-name-'+schema+'" >'+schema+'</div>'
          )
          tables = getTables(result, schema);     //function to get array of tables in schema
          for (var table of tables){          //nested loop to display tables for each schema
            $('#connection-tables').append(
              '<div class="row table-name" id="table-name-'+table+'" ><a href="#">'+table+'</a></div>'
            )
          }
        }
        $('#connection-tables').on('click', '.table-name', function(){
          var table = '';
          var columns = [];
          table = this.id.substring(11);
          columns = getColumns(result, table);
          $('#connection-columns').text('');
          $('#connection-columns').append(
            '<div class="row column-header">'+table+'</div>'
          );
          for (var column of columns){
            $('#connection-columns').append(
              '<div class="row column-name" id="column-name-'+column+'" ><a href="#">'+column+'</a></div>'
            );
          }
        });
      } else {
        $('#connection-message').text('Failed to Connect');
      }
    });
  });

  $('#queries-tab').click(function(){
    $('#queries-viewer').show();
    $('#schema-viewer').hide();
    $('#queries-tab').addClass('active');
    $('#connections-tab').removeClass('active');
  });

  $('#connections-tab').click(function(){
    $('#queries-viewer').hide();
    $('#schema-viewer').show();
    $('#queries-tab').removeClass('active');
    $('#connections-tab').addClass('active');
  });

  $('#query-list').on('click', '.query-name', function(){
    var queryId = '';
    queryId = this.id;
    $('.query-name').removeClass('query-name-selected');
    $('#'+queryId).addClass('query-name-selected');
    $('#query-btn-row').show();
  });

  $('#edit-query').click(function(){
    var queryId = '';
    queryId = $('#query-list').find('div.query-name-selected').attr('id');
    $('#query-display-name').val(queryId);
    $.get($SCRIPT_ROOT + '/api/queries/' + encodeURI(queryId), function(result){
      $('#query-writing-window').val(result);
    });
  });

  $('#clear-query').click(function(){
    $('#query-writing-window').val('');
    $('#query-display-name').val('');
  });

  $('#save-query').click(function(){
    var rawSql = '';
    var queryId = '';
    queryId = $('#query-display-name').val();
    rawSql = $('#query-writing-window').val();
    $('#query-save-response').show();
    if(queryId == ''){
      $('#query-save-response').text('Query Not Saved: Query Name cannot be blank.');
    } else if(rawSql == ''){
      $('#query-save-response').text('Query Not Saved: Query cannot be blank.');
    } else {
      $.post($SCRIPT_ROOT + '/api/queries/' + encodeURI(queryId), {'raw_sql': rawSql, 'query_name': queryId, 'delete_query': 'No'}, function(results){
        $('#query-save-response').text('Saved Succesfully');
        $('#query-list').text('');
        for (var result of results){
          $('#query-list').append('<a href="#"><div class="row query-name" id="'+result+'">'+result+'</div></a>')
        }
      }).fail(function(){
        $('#query-save-response').text('Error: Save Failed');
      });
    }
  });

  $('#delete-query').click(function(){
    var queryId = '';
    queryId = $('#query-list').find('div.query-name-selected').attr('id');
    $('#query-save-response').show();
    $.post($SCRIPT_ROOT + '/api/queries/' + encodeURI(queryId), {'delete_query': 'Yes', 'query_name': queryId, 'raw_sql': 'none'}, function(results){
      $('#query-save-response').text('Deleted Succesfully');
      $('#query-list').text('');
      $('#clear-query').click();
      for (var result of results){
        $('#query-list').append('<a href="#"><div class="row query-name" id="'+result+'">'+result+'</div></a>')
      }
    }).fail(function(){
      $('#query-save-response').text('Error: Delete Failed');
    });
  });


});

//This function takes a json of column names, table names, and schemas and
//returns an array of unique schema names
function getSchemas(arr){
  var dupeSchemas = [];
  var uniqueSchemas = [];
  for (var i of arr){
    dupeSchemas.push(i['table_schema']);
    //console.log(i);
  }
  uniqueSchemas = dupeSchemas.filter(uniqueFilter);
  return uniqueSchemas;
}

//This function takes a json of column names, table names, and schemas and
//a string of a schema name.  It returns an array of table names in that schema.
function getTables(data, schemaName){
  var filteredTableArray = [];
  var filteredTableObjects = [];
  var uniqueTables = [];
  filteredTableObjects = data.filter(function(object){
    return object['table_schema']===schemaName;
  });
  for (var i of filteredTableObjects){
    filteredTableArray.push(i['table_name']);
  }
  uniqueTables = filteredTableArray.filter(uniqueFilter);
  return uniqueTables;
}

function getColumns(data, tableName){
  var filteredColumnObjects = [];
  var filteredColumnArray = [];
  filteredColumnObjects = data.filter(function(object){
    return object['table_name']===tableName;
  });
  for (var i of filteredColumnObjects){
    filteredColumnArray.push(i['column_name']);
  }
  return filteredColumnArray;
}

//This function serves as an argument to the .filter method on arrays.  It
//filters an array to unique values.
function uniqueFilter(value, index, self) {
  return self.indexOf(value) === index;
}
