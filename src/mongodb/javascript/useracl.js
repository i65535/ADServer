useracl = function (user_id, level) {
	var getGroups = function(user_id){
		var arr = [];
		var cor = db.User_Group.find({'user_id':user_id});
		cor.forEach(function(rel){
			arr.push(rel.group_id);
		});
		return arr;
	}

	var data = {};
	var gids = getGroups(user_id);
	if (gids.length){
		var cor = db.Group_Namespace.find({'group_id':{'$in':gids}});
		cor.forEach(function(rel){
			if (rel.control >= level){
				if (! (rel.namespace in data && data[rel.namespace] > rel.control)){
					data[rel.namespace] = rel.control;
				}
			}
		});
	}

	if(level == 1){
		var cor = db.Namespace.find({'permission':'public'});
		cor.forEach(function(npc){
			if(! (npc._id in data)){
				data[npc._id] = 1;
			}
		});
	}

	return {"result":0, "content":data};
}
