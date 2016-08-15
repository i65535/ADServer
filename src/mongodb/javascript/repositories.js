repositories = function (query, size, skip, sorts) {
	var GetTags = function(repo_id){
		
		arr = []
		var corsur = db.Tags.find({'repository':repo_id, 'delete':0}, {'tag_name': 1,'create_time':1,'pull_num':1,'repository':1, 'digest':1}).sort({'_id': -1});
		corsur.forEach(function(tag){
			image = db.Image.findOne({"_id":tag.digest});
			if (image){
				tag['size'] = image['size'];
			}
			arr.push(tag);
		});
		return arr;
	}

	var GetPermission = function(namespace){
		var npc = db.Namespace.findOne({'_id':namespace});
		if (npc){
			return npc.permission;
		}
		return 'public';
	}

	var data = [];
	var total = db.Repository.count(query);
	var cor = db.Repository.find(query).sort(sorts).limit(size).skip(skip);
	cor.forEach(function(repo){
		var tags = GetTags(repo._id);
		if(tags.length){
			repo['tags'] = GetTags(repo._id);
			repo['permission'] = GetPermission(repo.namespace);
			data.push(repo);
		}
	});

	return {"result":0, "content":data, "total":total};
}
