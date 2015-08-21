function create_li_tags() {
    $.getJSON("/assets/js/tx3_tag_cloud.json", function(data){
	var items = [];
	$.each(data, function(key, val){
	    var count = val[0]
	    var url = val[1]
	    var posts = val[2]
	    items.push("<li data-weight='" + count + "'><a href='" + url + "'>" + key + "</a></li>");
	});

	$("<ul/>", {
	    "id": "tagcloud",
	    html: items.join("")
	}).appendTo("div.row");

	$("#tagcloud").tx3TagCloud({
	    multiplier: 5 // default multiplier is "1"
	});
    });
}
create_li_tags();
