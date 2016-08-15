popularTags = function (num) {

	var data = [];
	var cor = db.Tags.find({'delete':0}, {'repository': 1, 'tag_name':1, 'desc':1, 'pull_num':1}).sort({'pull_num':-1}).limit(num);
	cor.forEach(function(tag){
		data.push(tag);
	});

	return {"result":0, "content":data};
}
