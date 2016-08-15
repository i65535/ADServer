registryCounter = function (timestamp) {

	var data = {};
	data['pull'] = db.PullEvent.count({'pull_time':{'$gt':timestamp}});
	data['push'] = db.PushEvent.count({'push_time':{'$gt':timestamp}});

	return {"result":0, "content":data};
}
