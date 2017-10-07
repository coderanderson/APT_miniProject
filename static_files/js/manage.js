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
        for(var i=0; i<data.owned_streams.length; i++)
        {
            var s = data.owned_streams[i]
            var td = '<tr class="sstream_data"><td class="streamName" id="'+s.name+'">'+
                '<a href="/view_stream?stream_name='+s.name+'">'+s.name+'</a>'+
                '</td><td>'+s.last_new_photo_date+'</td>'+
                '<td>'+s.number_of_photos+'</td>'+
                '<td class="rightBoundry">'+
                '<input type="checkbox" id="checkbox"/></td></tr>'
            $('#owned_streams').append(td)
        }
        for(var i=0; i<data.subscribed_streams.length; i++)
        {
            var s = data.subscribed_streams[i]
            var td = '<tr class="sstream_data"><td class="streamName" id="'+s.name+'">'+
                '<a href="/view_stream?stream_name='+s.name+'">'+s.name+'</a>'+
                '</td><td>'+s.last_new_photo_date+'</td>'+
                '<td>'+s.number_of_photos+'</td>'+
                '<td>'+prettifyNumber(s.number_of_views)+'</td><td class="rightBoundry">'+
                '<input type="checkbox" id="checkbox"/></td></tr>'
            $('#subscribed_streams').append(td)
        }
    });
}


function getCheckedStream(className, action) {
    var result=[]
    $("."+className).each(function(i,item){
        
        sname = $(item).find('.streamName').html()
        scheck = $(item).find('#checkbox').is(":checked")
        if(scheck)
        {
            result.push(sname)
            $(item).hide()
            if(className=='ostream_data')
                $('.sstream_data').has('#'+sname).hide()
        }
    })
    result=result.join(',')
    $.post(action,{streams: result}, function(data, status){
        setTimeout(function(){location.reload()}, 1);
    })
}

$(document).ready(function(){
    getManagementData();
    $("#delete_btn").click(function(){getCheckedStream('ostream_data','/api/delete_streams')})
    $("#unsubscribe_btn").click(function(){getCheckedStream('sstream_data','/api/unsubscribe_streams')})
});
