function makeAjaxRequest(course_id){
    $.ajax({
        method: "GET",
        url: url + '?id=' + course_id,
        success: function(data){
            data = data['results'][0];
        },
        error: function (error_data) {
            // console.log("error");
        }
    });
}

function getTimeToLeave(departure) {
    // 0 - hour, 1 - minutes
    let tmp = departure[1] - travel_duration;
    let result = [];

    if(tmp < 0){
        if(departure[0] === 0)
            result[0] = 23;
        else
            result[0] = departure[0]-1;
        result[1] = 60 + tmp;
    }
    else {
        result[0] = departure[0];
        result[1] = tmp;
    }

    return result;
}

function renderHTML(data) {
    let htmlString = "";
    htmlString+='<h4>' + data['departure'] + '</h4>';
    if(walking_directions){
    let departure = data['departure'].split(':');
    departure = [parseInt(departure[0]), parseInt(departure[1])];
    let time_to_leave = getTimeToLeave(departure);
    htmlString+='<i> Wyjdź o ' + time_to_leave.join(':') + '</i>';
    $("#id_left_col").html(htmlString);
    // htmlString='';
    // htmlString+='<h4> XX:XX</h4>';
    // $("#id_right_col").html(htmlString);
    }


    htmlString="<i id=\"id_circle\" class=\"fa fa-2x fa-arrow-circle-right rotate\"></i>";
    htmlString+='<h5><i class="fas fa fa-bus"></i>' + data['carrier'] + '</h5>';
    if(data['line'])
        htmlString+='<h5>' + data['line'] + '</h5>';
    $("#id_mid_col").html(htmlString);
}


url = 'http://127.0.0.1:8000/bushelper/restapi/courses';
let course_list_item = $(".course_list_item");
let course_panel;


course_list_item.mouseover(function () {
        $(this).css({"background-color":"#E8F1FA", "transition":"background-color 0.5s ease", "cursor": "pointer"});
});

course_list_item.mouseleave(function () {
    if(!$(this).hasClass('course_panel'))
        $(this).css({"background-color":"#f8f8f8", "transition":"background-color 0.5s ease", "cursor": ""});
});

$(window).ready(function() {
    let first_li = $("#courses_list li").first();
    first_li.css({"background-color":"#E8F1FA", "transition":"background-color 0.5s ease", "cursor": "pointer"});
    first_li.addClass('course_panel');
    let  first_li_id =  first_li.attr('id');
    first_li_id =  first_li_id.split('_')[2];
    makeAjaxRequest(first_li_id);


});

course_list_item.click(function () {
    course_panel = $(".course_panel");
    course_panel.removeClass('course_panel');
    course_panel.addClass('course_list_item');
    course_panel.css({"background-color":"#f8f8f8", "transition":"background-color 0.5s ease", "cursor": ""});
    $(this).addClass('course_panel');
    let this_id = $(this).attr('id');
    this_id = this_id.split('_')[2];
    makeAjaxRequest(this_id);
});