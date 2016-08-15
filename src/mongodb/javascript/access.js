access = function (user_id, namespace) {
	var acl = [];
	var npc = db.Namespace.findOne({"_id":namespace});
	if (npc && npc.permission == 'public'){
		acl.push(1);
	}

	var getGroups = function(user_id){
		var arr = [];
		var cor = db.User_Group.find({'user_id':user_id});
		cor.forEach(function(rel){
			arr.push(rel['group_id']);
		});
		return arr;
	}
	var group_list = getGroups(user_id);
	if(group_list.length < 1){
		return {"result":0, "content":acl};
	}
	
	var cor1 = db.Group_Namespace.find({"namespace":namespace,'group_id':{'$in':group_list}});
	cor1.forEach(function(rel){
		acl.push(rel['control']);
	});

	return {"result":0, "content":acl};
}
 