
var full_texts;
$(document).ready(function () {
    $("#introduction").hide();
    $("#mlbirs_full").hide();
    $("#full_texts").hide();
    $("#full_text").hide();

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

                // TODO: scrable texts from task to task
            },
            error: function (e) {
                console.log("ERROR : ", e);

            }
        });

    $("#btn-introduction").click(function (event) {

        console.log("click html1");
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
            $("#all-text").text(function(){
                console.log(alltext);
                return alltext
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

