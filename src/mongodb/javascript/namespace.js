namespace = function (space_id) {
	var getGroupData = function(space_id){
		var arr = [];
		var cor = db.Group_Namespace.find({'namespace':space_id});
		cor.forEach(function(rel){
			var group_name = '';
			group = db.Group.findOne({'_id':rel.group_id},{'group_name': 1});
			if (group)
			{
				group_name = group.group_name;
			}
			arr.push({'group_id':rel.group_id,'control':rel.control,'group_name':group_name});
		});
		return arr;
	}

	var info = db.Namespace.findOne({"_id":space_id});
	if(info){
		info['repo_num'] = db.Repository.count({'namespace':space_id, 'empty':false});
		info['groups'] = getGroupData(space_id);
		return {"result":0, "content":info};
	}
	else{
		return {"result":1};
	}
	
}
 