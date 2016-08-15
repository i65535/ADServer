groups = function (query, size, skip) {
	var getGroups = function(filter){
		var arr = [];
		var cor = db.Group_Namespace.find(filter);
		cor.forEach(function(rel){
			arr.push(rel.group_id);
		});
		return arr;
	}
	var condition = {};
	if(query && query.namespace){
		var id_list = getGroups(query);

		if (id_list.length < 1)
		{
			return {"result":0, "content":[]};
		}

		condition = {'_id':{'$in':id_list}};
	}

	var groups = [];
	var cor = db.Group.find(condition);
	cor.forEach(function(grp){
		grp['user_num'] = db.User_Group.count({'group_id':grp._id});
		groups.push(grp);
	});
	
	return {"result":0, "content":groups};
	
}
 