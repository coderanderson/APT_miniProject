var ownName = true;
var ownPicture = true;
var subscribeName = true;
var subscribeNumber = true;
var subscribeView = true;

var owned_streams = 0;
var subscribed_streams = 0;

function sort_owned_streams_name(s) {
    if(ownName)
        owned_streams.sort(sortNameUp);
    else 
        owned_streams.sort(sortNameDown);
}

function sort_owned_streams_number(s) {
    if(ownPicture)
        owned_streams.sort(sortNumberUp);
    else 
        owned_streams.sort(sortNumberDown);
}

function sort_subscribed_streams_name(s) {
    if(subscribeName)
        subscribed_streams.sort(sortNameUp);
    else
        subscribed_streams.sort(sortNameDown);
}

function sort_subscribed_streams_number(s) {
    if(subscribeNumber)
        subscribed_streams.sort(sortNumberUp);
    else
        subscribed_streams.sort(sortNumberDown);
}

function sort_subscribed_streams_view(s) {
    if(subscribeView)
        subscribed_streams.sort(sortViewUp);
    else
        subscribed_streams.sort(sortViewDown);
}

function sortNameUp(a, b) {
    if (a.name.localeCompare(b.name) == -1) return -1;
    else if (a.name.localeCompare(b.name) == 1) return 1;
    else return 0;
}

function sortNameDown(a, b) {
    if (a.name.localeCompare(b.name) == -1) return 1;
    else if (a.name.localeCompare(b.name) == 1) return -1;
    else return 0;
}

function sortNumberUp(a, b) {
    if(a.number_of_photos == b.number_of_photos) return 0;
    else if(a.number_of_photos < b.number_of_photos) return -1;
    else return 1;
}

function sortNumberDown(a, b) {
    if(a.number_of_photos == b.number_of_photos) return 0;
    else if(a.number_of_photos < b.number_of_photos) return 1;
    else return -1;
}

function sortViewUp(a, b) {
    if(a.number_of_views == b.number_of_views) return 0;
    else if(a.number_of_views < b.number_of_views) return -1;
    else return 1;
}

function sortViewDown(a, b) {
    if(a.number_of_views == b.number_of_views) return 0;
    else if(a.number_of_views < b.number_of_views) return 1;
    else return -1;
}

$("#ownNameButton").click(function () {
    if(ownName === true) ownName = false;
    else ownName = true;
    sort_owned_streams_name();
    getManagementData();
})

$("#ownPictureButton").click(function () {
    if(ownPicture === true) ownPicture = false;
    else ownPicture = true;
    sort_owned_streams_number();
    getManagementData();
})

$("#subscribeNameButton").click(function () {
    if(subscribeName === true) subscribeName = false;
    else subscribeName = true;
    sort_subscribed_streams_name();
    getManagementData();
})

$("#subscribeNumberButton").click(function () {
    if(subscribeNumber === true) subscribeNumber = false;
    else subscribeNumber = true;
    sort_subscribed_streams_number();
    getManagementData();
})

$("#subscribeViewButton").click(function () {
    if(subscribeView === true) subscribeView = false;
    else subscribeView = true;
    sort_subscribed_streams_view();
    getManagementData();
})

$(".sortButton").click(function () {
    $(this).text(function(i, v){
       return v === "\u25B2" ? "\u25BC" : "\u25B2"
    })
});

function prettifyNumber(num){
    if(num<1000)
        return ''+num
    if(num<1000000)
        return ''+Math.round(num/1000)+'K'
    else
        return ''+Math.round(num/1000000)+'M'
}

function getManagementData(){
    $.post("/api/management_data",{}, function(data, status){

        for(var i=0; i<owned_streams.length; i++)
        {
            var s = owned_streams[i]
            var td = '<tr class="ostream_data"><td class="streamName" id="'+s.name+'">'+
                '<a href="/view_stream?stream_name='+s.name+'">'+s.name+'</a>'+
                '</td><td>'+s.last_new_photo_date+'</td>'+
                '<td>'+s.number_of_photos+'</td>'+
                '<td class="rightBoundry">'+
                '<input type="checkbox" id="checkbox"/></td></tr>'
            if(i === 0) $(".ostream_data").remove();
            $('#owned_streams').append(td)
        }
        for(var i=0; i<subscribed_streams.length; i++)
        {
            var s = subscribed_streams[i]
            var td = '<tr class="sstream_data"><td class="streamName" id="'+s.name+'">'+
                '<a href="/view_stream?stream_name='+s.name+'">'+s.name+'</a>'+
                '</td><td>'+s.last_new_photo_date+'</td>'+
                '<td>'+s.number_of_photos+'</td>'+
                '<td>'+prettifyNumber(s.number_of_views)+'</td><td class="rightBoundry">'+
                '<input type="checkbox" id="checkbox"/></td></tr>'
            if(i === 0) $(".sstream_data").remove();
            $('#subscribed_streams').append(td)
        }
    });
}

function initialize(){
    $.post("/api/management_data",{}, function(data, status){
        //alert("hello");
        owned_streams = data.owned_streams;
        subscribed_streams = data.subscribed_streams;
    });
}

initialize();


function getCheckedStream(className, action) {
    var result=[]
    $("."+className).each(function(i,item){
        
        sname = $(item).find('.streamName a').html()
        scheck = $(item).find('#checkbox').is(":checked")
        if(scheck)
        {
            result.push(sname)
            $(item).hide()
            if(className=='ostream_data') {
                $('.sstream_data').has('#'+sname).hide()
            }
        }
    })
    result=result.join(',')
    $.post(action,{streams: result}, function(data, status){
        setTimeout(function(){location.reload()}, 1);
    })
}

$(document).ready(function(){
    //alert(owned_streams[0]);
    getManagementData();
    $("#delete_btn").click(function(){getCheckedStream('ostream_data','/api/delete_streams')})
    $("#unsubscribe_btn").click(function(){getCheckedStream('sstream_data','/api/unsubscribe_streams')})
});
