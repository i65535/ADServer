groupInfo = function (group_id) {
	var getUserData = function(gid){
		var arr = [];
		var cor = db.User_Group.find({'group_id':gid});
		cor.forEach(function(rel){
			user = db.User.findOne({"_id":rel.user_id});
			if(user){
				arr.push(user._id + ':'+ user._id);
			}
		});
		return arr.join('#');
	}

	var info = db.Group.findOne({"_id":group_id});
	if(info){
		info['users'] = getUserData(group_id);
		return {"result":0, "content":info};
	}
	else{
		return {"result":1};
	}
	
}
 