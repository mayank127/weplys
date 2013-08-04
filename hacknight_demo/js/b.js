
	var songInfo=new Array();
	
function loadFile(input) {
	//console.log("HERE");
	var j =0;
	var url=new Array();

	var file=new Array();
	
	for (var i = 0; i < input.files.length; i++) {
		file[i] = input.files[i];
		url[i] = file[i].urn || file[i].name;
	}
	var f = function(i){
		if(i!=input.files.length){
			var reader = new FileReader();
			reader.onload = function(event) {
				ID3.loadTags(url[i], function() {
				  showTags(url[i]);
					f(i+1);
				}, {
				  tags: ["title","artist","album","picture"],
				  dataReader: FileAPIReader(file[i])
				});
			};
			reader.readAsArrayBuffer(file[i]);
		}
		else{
			setInfo(songInfo);
		}
	}
	f(0);
}

function showTags(url) {
	 // console.log(url);
	  var tags = ID3.getAllTags(url);
	  console.log(tags);
	  var info=new Array();
	  info.push(url);
	  info.push(tags.title);
	  info.push(tags.artist);
	  info.push(tags.album);
	  info.push(tags.picture);
	  
	 songInfo.push(info);	 
}