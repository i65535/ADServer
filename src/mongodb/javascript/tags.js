tags = function (query, size, skip) {
	var data = [];
	var cor = db.Tags.find(query).limit(size).skip(skip);
	cor.forEach(function(tag){
		image = db.Image.findOne({"_id":tag.digest});
		if (image){
			tag['size'] = image['size'];
		}
		var arr = tag.repository.split('/');
		if (arr.length > 1){
			npc = db.Namespace.findOne({"_id":arr[0]});
			if (npc){
				tag['permission'] = npc['permission'];
			}
		}
		else{
			tag['permission'] = 'public';
		}

		data.push(tag);
	});

	return {"result":0, "content":data};
}
