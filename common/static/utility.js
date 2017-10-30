/*******************************************************************************
COMMON/STATIC/UTILITY.js
*******************************************************************************/


function cl(p_msg)
{
    console.log(p_msg)
}

function ErrorToStatus(p_error, p_func, p_status)
{
    var msg = DjangoSubError(p_error);
    cl(msg);
    
    if (msg.length < p_error.length)
    {
        msg = p_func + "<br>" + msg;
        $(p_status).html(msg);
    }
    else
    {
        $(p_status).css('white-space', 'pre-line');
        msg = p_func + "\n" + msg;
        $(p_status).text(msg);  
    }
    $(p_status).parent().parent().show(); 
    $(p_status).parent().css('background-color', '#ffb3db');  //deeppink  
    $(p_status).parent().css('text-align', 'right');  
    $(p_status).parent().css('padding', '2px 4px'); 
}

function DjangoSubError(p_err)
{
    bg = p_err.search("Traceback");            
    nd = p_err.search("Request information");
    subErr = p_err;
    
    if (bg > 0)
    {
        subErr = p_err.substring(bg, nd);
        subErr = subErr.replace(/\. /g, ".<br>");
    }
    
    return subErr;
}


function GetRandomInt(min, max)
{
    // inclusive of end-points
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function SecondsToTimeDelta(p_secs)
{
    var timeDelta = {
        'hours': Math.floor(p_secs / 60 / 60),
        'minutes': Math.floor( (p_secs / 60) % 60 ), 
        'seconds': Math.floor(p_secs % 60),
    };
        
    return timeDelta;
}


/*******************************************************************************
STRINGS
*******************************************************************************/


function Pad2(p_num)
{
    var num = p_num.toString();
    if (num.length == 1 )
        return "0" + p_num.toString();    
    return p_num.toString();
}

function FormatFileName(p_msg)
{
    var frm = String(p_msg).toLowerCase();
    frm = frm.replace(" ", "_");
    frm = frm.replace("[", "");
    frm = frm.replace("]", "");
    return frm;
}

function TitleCase(value)
{
    //words = value.toLowerCase().split(' ');
    var words = value.split(' ');
    for(var i = 0; i < words.length; i++) {
        var letters = words[i].split('');
        letters[0] = letters[0].toUpperCase();
        words[i] = letters.join('');
    }
    return words.join(' ');
}

String.prototype.format = function()
{
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
}

String.prototype.replaceAll = function(search, replacement)
{
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
}


/*******************************************************************************
JQUERY DATATABLES
*******************************************************************************/


function JSONtoFullTable(listJSON)
{
    // create the column names
    
    var cols = []
    var data1 = listJSON[0];
    
    for (var key in data1)
    {
        var title = key.replace(/_/g, " ");
        title = TitleCase(title);
        cols.push(title);
    }
    
    // create records array
    
    var recs = [];
    
    listJSON.forEach( function (obj)
    {
        var newRow = [];
        for (var key in obj)
        {
            var value = obj[key];
            newRow.push(value);
        }
        recs.push(newRow);
    });
    
    // display data on table
    
    var fullTable = {'columns': cols, 'records': recs};
    
    return fullTable;
}

function JObjToFullTable(jObj)
{
    // create the column names
    
    var cols = []
    
    for (var key in jObj)
    {
        var title = key.replace(/_/g, " ");
        title = TitleCase(title);
        cols.push(title);
    }
    
    // create records array
    
    var recs = [];
    
    var newRow = [];
    for (var key in jObj)
    {
        var value = jObj[key];
        newRow.push(value);
    }
    recs.push(newRow);
    
    // display data on table
    
    var fullTable = {'columns': cols, 'records': recs};
    
    return fullTable;
}


function CheckForErrors(p_tableID, p_fullTable)
{
    if ($(p_tableID).length === 0) 
        return "Table HTML-ID not found:" + p_tableID;
    
    if (!p_fullTable)
        return "Data parameter is null.";
    
    if (!p_fullTable.hasOwnProperty("columns") || !p_fullTable.hasOwnProperty("records")) 
        return "Data doesn't have FullTable format.";
    
    if (p_fullTable.columns.length === 0 || p_fullTable.records.length === 0) 
        return "FullTable has no records.";
    
    return null;
}

function SetDataTableColumns(p_tableID, p_columns)
{
    var tableHtml = '';
    tableHtml += '<thead>\n';
    tableHtml += '   <tr role=\'row\'>\n';    
    
    for (var c = 0; c < p_columns.length; c++) {
        tableHtml += '      <th class=\'\' style=\'text-align: left; padding: 8px 10px;\'>' + p_columns[c] + '</th>\n';
    }
    
    tableHtml += '   </tr>\n';
    tableHtml += '</thead>\n';
    
    $(p_tableID).html(tableHtml);
}

function SetDataTable(p_tableID, p_fullTable, p_colsClass, p_hlValue)
{
    p_colsClass = p_colsClass || {};
    p_hlValue = p_hlValue || "";

    var errors = CheckForErrors(p_tableID, p_fullTable);
    if (errors) {
        console.log(errors);
        return;   
    }
    
    SetDataTableColumns(p_tableID, p_fullTable.columns);    
    
    var colDefs = [];
    $.each(p_fullTable.columns, function(idx, val) {
        var colDef = { aTargets: [idx,] };
        $.each(p_colsClass, function(key, val2) {
            if (val.toLowerCase() == key.toLowerCase().replace(/_/g, " ")) {
                colDef['sClass'] = val2;
            }
        });
        colDefs.push(colDef);
    });
    
    $(p_tableID).DataTable( {
        data: p_fullTable.records,
        aoColumnDefs: colDefs,
        bSort: false,
        scrollCollapse: true,
        paging: false,
        bFilter: false,
        bInfo: false,
        bAutoWidth: false,
        bDestroy: true,        // necessary to refresh the data
        "createdRow": function( row, data, dataIndex ) {            
            if ( p_hlValue && $.inArray(p_hlValue, data) >= 0 )   // inArray returns the index
            {
                $(row).children().each(function (index, td) {
                       $(this).addClass('format_highlight');
                });
            }
        },
    } );
    
}


function TransposeFullTable(p_fullT)
{
    var cols = ["Property", "Value"];
    var values = [];
    var conv = {columns: cols, records: values};
    
    if (p_fullT.records.length == 0)
        return conv;
    
    for (var c = 0; c < p_fullT.columns.length; c++)
    {
        var prop = p_fullT.columns[c];
        var value = p_fullT.records[0][c];
        var row = [prop, value];
        values.push(row);        
    }
    
    return conv;
}

function SetVerticalTable(p_tableID, p_fullTable)
{
    var errors = CheckForErrors(p_tableID, p_fullTable);
    if (errors) {
        cl(errors);
        return;   
    }
        
    // set the transposed full-table with jquery datatables 
    
    $(p_tableID).DataTable( {
        data: p_fullTable.records,
        aoColumnDefs: [
            {
                aTargets: [0],
                sClass: "table_cell",
                mRender: function (data, type, full) {
                    html = '<div style="white-space: nowrap;">';
                    html += '<b>' + data + '</b>';
                    html += '</div>';
                    return html;
                },  
            },
            {
                aTargets: [1],
                sClass: "table_cell",
            } 
        ],
        bSort: false,
        scrollCollapse: true,
        paging: false,
        bFilter: false,
        bInfo: false,
        bAutoWidth: false,
        bDestroy: true,                 // necessary to refresh the data
        fnDrawCallback: function() {
            // remove headers
            $(p_tableID + ' thead').remove();
        },
    } );
    
}



/*******************************************************************************
DOM MANIPULATION
*******************************************************************************/


function MakeDialog(p_elemID, p_width, p_closeBtn)
{
    // old IE can't handle function default parameters
    p_width = p_width || 'auto';
    p_closeBtn = p_closeBtn || true;
    
    var openFnc = null;

    if (!p_closeBtn)
        openFnc = function(event, ui) {
            $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
        };

    $(p_elemID).dialog({
        'autoOpen': false,
        'draggable': false,
        'resizable': false,
        'modal': true,        // can only focus on this 
        'width': p_width,
        'closeOnEscape': false,
        'open': openFnc,
    });
}


function CreateTooltip(p_elemId, p_message, p_position)
{
    p_position = p_position || 'right';
    
    if (p_position == "left")
        pos = {my: 'right center', at: 'left+5% center'}
    
    else if (p_position == "top")
        pos = {my: 'center bottom', at: 'center top+5%'}
    
    else if (p_position == "bottom")
        pos = {my: 'center top', at: 'center bottom+5%'}
    
    else 
        pos = {my: 'left center', at: 'right+5% center'}
    
    $(p_elemId).tooltip({
        items: p_elemId,
        tooltipClass: 'jqueryUI_tooltip',
        content: p_message,
        position: pos,
    });
}


$.fn.insertAtIndex = function(index,selector)
{
    var opts = $.extend({
        index: 0,
        selector: '<div/>'
    }, {index: index, selector: selector});

    return this.each(function() {
        var p = $(this);  
        var i = ($.isNumeric(opts.index) ? parseInt(opts.index) : 0);
        if(i <= 0)
            p.prepend(opts.selector);
        else if( i > p.children().length-1 )
            p.append(opts.selector);
        else
            p.children().eq(i).before(opts.selector);       
    });
}



/*******************************************************************************
AJAX AUTHENTICATION
*******************************************************************************/


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


/*******************************************************************************
END OF FILE
*******************************************************************************/