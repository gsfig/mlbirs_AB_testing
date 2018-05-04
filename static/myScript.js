
// TODO: join full texts from full mlbirs and full-texts

var full_texts;
var stop_words;
$(document).ready(function () {
    $("#introduction").hide();
    $("#mlbirs_full").hide();
    $("#full_texts").hide();
    $("#full_text").hide();

    $.ajax({ // get all ids and texts and store to var full_texts
            type: "GET",
            //enctype: 'multipart/form-data',
            url: "get_stop_words",
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            success: function (stop_w) {
                // console.log("SUCCESS : ", stop_w);
               stop_words = JSON.parse(stop_w);
               // console.log("SUCCESS : ", stop_words);
               //  prepare_pattern()
            },
            error: function (e) {
                console.log("ERROR : ", e);

            }
        });





    $.ajax({ // get all ids and texts and store to var full_texts
            type: "GET",
            //enctype: 'multipart/form-data',
            url: "get_docs",
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            success: function (id_and_texts) {
                //console.log("SUCCESS : ", id_and_texts);
                full_texts = JSON.parse(id_and_texts);

                // TODO: scramble texts from task to task
            },
            error: function (e) {
                console.log("ERROR : ", e);

            }
        });

    $("#btn-introduction").click(function (event) {

        $("#mlbirs_full").hide();
        $("#full_texts").hide();
        $("#introduction").show();
    });
    $("#btn-mlbirs-full").click(function (event) {

        $("#introduction").hide();
        $("#full_texts").hide();
        $("#mlbirs_full").show();
    });
    $("#btn-full_texts").click(function (event) {

        $("#introduction").hide();
        $("#mlbirs_full").hide();

        show_full_texts();

        $("#full_texts").show();
    });

});

function showError() {
}

function show_full_texts(){
    //console.log(full_texts);
    $("#texts-table").tabulator({
        height:150, // set height of table, this enables the Virtual DOM and improves render speed dramatically (can be any valid css height value)
        layout:"fitColumns", //fit columns to width of table (optional)

        columns:[ //Define Table Columns
            {title:"Summary", field:"doc_text", align:"center", headerSort:false}
        ],
        initialSort:[
            //{column:"average_score", dir:"desc"}, //sort by this first
            //{column:"doc_text", dir:"desc"}, //then sort by this second
        ],
        rowClick:function(e, row){ //trigger this when the row is clicked
            $("#full_text").show();

            var alltext = row.getData().doc_text;
            $("#all-text").html(function(){
                // console.log(format_text(alltext));

                return format_text(alltext);
            });

        }

    });
    //define data
    var tablescores = [];

    for(var x in full_texts){ // json to array
        //console.log(full_texts[x])
        tablescores.push(full_texts[x]);
    }

    //load sample data into the table
    $("#texts-table").tabulator("setData", tablescores);
    // $("#example-table").tabulator("setFilter", "average_score", ">", 0.5);

}

function format_text(text_to_format){

    var re;
    var stop_w;
    var replacement;
    for(stop_w in stop_words){
        re = new RegExp(stop_words[stop_w], "g");
        replacement = "<br> <span class=\'title\'>".concat(stop_words[stop_w]).concat("<br> </span>");

        text_to_format = text_to_format.replace(re,replacement);
    }
    return text_to_format;
}


