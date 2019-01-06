function filterData(data) {

    let full_stop_name;
        for(i = 0; i<data.length; i++)
            if(data[i]['direction'] === direction.val()) {
                if (data[i]['fremiks_alias'] && data[i]['fremiks_alias'] !== data[i]['mpk_street'])
                    full_stop_name = data[i]['mpk_street'] + ' ' +  data[i]['fremiks_alias'];
                else
                    full_stop_name = data[i]['mpk_street'];
                tags.push({label: full_stop_name, value: data[i]['mpk_street']});
            }
        console.log(tags);
        let len = data.length;
        origin.autocomplete({
            source: function(request, response) {
                let results = $.ui.autocomplete.filter(tags, request.term);
                response(results.slice(0, 10));
                },
        });
        destination.autocomplete({
            source: function(request, response) {
                let results = $.ui.autocomplete.filter(tags, request.term);
                response(results.slice(0, 10));
                },
        });
}

let tags = [];
let origin = $('#id_origin');
let destination = $('#id_destination');
let direction = $("#id_direction");
let url_origin = 'https://bushelper.herokuapp.com/bushelper/restapi/busstops';
// TODO heroku
// let url_origin = 'http://127.0.0.1:8000/bushelper/restapi/busstops';

$.ajax({
    method: "GET",
    url: url_origin,
    success: function(data){
        console.log('success');
        filterData(data);
    },
    error: function (error_data) {
        console.log("error");
    }
});

direction.change(function () {
    origin.val("");
    destination.val("");
   let request = new XMLHttpRequest();
   request.open("GET", url);
   request.onload = function () {
       let data = JSON.parse(request.responseText);
       filterData(data);
   };
   request.send();
});