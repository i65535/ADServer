overview = function () {
	var data = {};
	data['namespace'] = db.Namespace.count();
	data['user'] = db.User.count();
	data['repository'] = db.Repository.count({'empty':false});

	return {"result":0, "content":data};
}