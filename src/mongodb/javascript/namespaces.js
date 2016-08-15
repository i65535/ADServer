namespaces = function (filter, size, skip, sort) {
	var getGroups = function(user_id){
		var arr = [];
		var cor = db.User_Group.find({'user_id':user_id});
		cor.forEach(function(rel){
			arr.push(rel.group_id);
		});
		return arr;
	}
	var getNameSpace = function(group_id_list){
		var arr = [];
		var cor = db.Group_Namespace.find({'group_id':{'$in':group_id_list}});
		cor.forEach(function(rel){
			arr.push(rel.namespace);
		});
		return arr;
	}

	var data = [];
	var conditions = [];
	if (filter.user_id)
	{
		conditions.push({'_id':filter.user_id});
		conditions.push({'permission':'public'});
		var ids = getGroups(filter.user_id);
		if (ids.length)
		{
			var nids = getNameSpace(ids);
			if(nids.length){
				conditions.push({'_id':{'$in':nids}});
			}
		}
	}

	var query = {};
	if(conditions.length > 1){
		query = {'$or':conditions};
	}
	else if(conditions.length == 1){
		query = conditions[0];
	}

	var total = db.Namespace.find(query).count();
	var cor = db.Namespace.find(query).sort(sort).limit(size).skip(skip);
	cor.forEach(function(nspc){
		nspc['repo_num'] = db.Repository.count({'namespace':nspc._id, 'empty':false});
		data.push(nspc);
	});

	return {"result":0, "content":data, 'total':total};
}
