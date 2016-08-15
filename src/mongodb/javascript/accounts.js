accounts = function (group_id, filter, size, skip) {
	var getUsers = function(group_id){
		var arr = [];
		var cor = db.User_Group.find({'group_id':group_id});
		cor.forEach(function(rel){
			arr.push(rel['user_id']);
		});
		return arr;
	}
	if (group_id >= 0){
		var user_list = getUsers(group_id);
		if(user_list.length < 1){
			return {"result":0, "content":[]};
		}
		filter['_id'] = {'$in':user_list};
	}

	var users = [];
	var cor1 = db.User.find(filter,{'password': 0}).limit(size).skip(skip);
	cor1.forEach(function(u){
		u['group_num'] = db.User_Group.count({'user_id':u._id});
		users.push(u);
	});

	return {"result":0, "content":users};
}
 