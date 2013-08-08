var currentPlaylist = []
var loadMusic = new Bacon.Bus();
var changeSong = new Bacon.Bus();
var files = $("#songFiles").asEventStream('change').map(function(object){
	return object.target.files;
});
var shuffle = $("#shuffle").asEventStream('click').map();
shuffle.assign(function(){
	currentPlaylist=shuffle(currentPlaylist);
	addToList();
	load();
	// Load in the first track
	$('ol li').first().addClass('playing');
	changeSong.push(currentPlaylist[0].id);
});
loadMusic.plug(files);
loadMusic.assign(function(data){
	currentPlaylist = []
	for (var i = 0; i < data.length; i++) {
		var file = data[i];
		var url = window.URL || window.webkitURL;
		var src = url.createObjectURL(file);
		currentPlaylist.push({
			src: src,
			name: file.name,
			id: i,
			file: file,
		});
	};
	addToList();
	load();
	// Load in the first track
	$('ol li').first().addClass('playing');
	changeSong.push(0);
});

var audio = audiojs.createAll({
  trackEnded: function() {
    var next = $('ol li.playing').next();
    if (!next.length) next = $('ol li').first();
    next.addClass('playing').siblings().removeClass('playing');
    changeSong.push($('a',next).attr('data-id'));
  }
})[0];

var load = function(){
	var clickSong = $('ol li').asEventStream('click').map(function(object){
		object.preventDefault();
	  	$(object.currentTarget).addClass('playing').siblings().removeClass('playing');
	  	var current = $('ol li.playing')
		return $('a', current).attr('data-id');
	});
	changeSong.plug(clickSong);
	changeSong.assign(playSong);
}
var addToList = function(){
   	$('#Playlist').empty();
  	for(var i=0;i<currentPlaylist.length;i++){
    	$('#Playlist').append("<li><a href='#' id="+i+" data-src='' data-id=" + currentPlaylist[i].id +">"+currentPlaylist[i].name+"</a></li>")
    	$('#'+i+'').attr('data-src', currentPlaylist[i].src);
    }
}
var shuffle = function(o){
    for(var j, x, i = o.length; i; j = Math.floor(Math.random() * i), x = o[--i], o[i] = o[j], o[j] = x);
    return o;
}

var loadFileData = function(file) {
	var reader = new FileReader();
	var url=file.urn || file.name;
	reader.onload = function(event) {
		ID3.loadTags(url, function() {
			var tags = ID3.getAllTags(url);
			$("#songname").html(tags.title);
      		$("#artist").html(tags.artist);
      		$("#album").html(tags.album);
      		var image = tags.picture;
  			if (image)
	   			var base64 = "data:" + image.format + ";base64," + Base64.encodeBytes(image.data);
			$("#albumimage").attr('src',base64);
			$("#albumimage").height($("#albumInfo").height());

			var ajaxInfo = Bacon.fromPromise(addSong({
				songname: tags.title,
				artistname: tags.artist,
			}));
			ajaxInfo.assign(function(data){
				console.log(data);
				$("#songname").html(data.song.songname);
	      		$("#artist").html(data.song.artist);
	      		$("#album").html(data.song.album);
				var lyrics = Bacon.fromPromise(getLyrics(data.song.songname));
				lyrics.assign(function(data){
					console.log(data);
					$("#lyrics").html(data.lyrics);
				});
			});
		}, {
		  tags: ["title","artist","album","picture"],
		  dataReader: FileAPIReader(file)
		});
	};
	reader.readAsArrayBuffer(file);
}

var playSong = function(j){
	for (var i = currentPlaylist.length - 1; i >= 0; i--) {
		if (currentPlaylist[i].id==j){
			audio.load(currentPlaylist[i].src);
	    	audio.play();
			loadFileData(currentPlaylist[i].file);
		}
	};
}

var addSong = function(song){
	var songInfo;
	data = {
		'song' : JSON.stringify(song),
        'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val(),
    };
	return $.ajax(
    {
        'type': 'POST',
        'url': '/add_song/',
        'data': data,
        'dataType': 'json',
    }).then(function(data) {
        return data;
    });
}

var getLyrics = function(songname){
	var songInfo;
	data = {
		'song' : JSON.stringify(songname),
        'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val(),
    };
	return $.ajax(
    {
        'type': 'POST',
        'url': '/get_lyrics/',
        'data': data,
        'dataType': 'json',
    }).then(function(data) {
        return data;
    });
}

var toggleFlag = [];
toggleFlag['stats']=0;
toggleFlag['recs']=0;
toggleFlag['lists']=0;
toggleFlag['Allsongs']=0;
$("#stats").click(function(){
  $(".stat").toggle("slow");
});
 	$("#recs").click(function(){
  $(".rec").toggle("slow");
});
 	$("#lists").click(function(){
  $(".list").toggle("slow");
});
 	$("#Allsongs").click(function(){
  $(".Allsong").toggle("slow");
});


