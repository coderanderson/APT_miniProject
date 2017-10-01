$(".sortButton").click(function () {
    $(this).text(function(i, v){
       return v === "\u25B2" ? "\u25BC" : "\u25B2"
    })
});
