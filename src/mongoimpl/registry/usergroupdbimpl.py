# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli, Result
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, USER_GROUP_TABLE, ID


class UserGroupDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = USER_GROUP_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        '''
        Limits application to single instance
        '''
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    
    def create_relation(self, group_id, user_id_list):
        arr = []
        for user_id in user_id_list:
            arr.append({'user_id':user_id, 'group_id':group_id, 'join_time':NowMilli()})
            
        return self.batch_insert(arr)
    
    
    def update_relation(self, group_id, user_id_list):
        rlt = self.read_record_list({'group_id':group_id})
        if not rlt.success:
            Log(1, 'UserGroupDBImpl.update_relation read_record_list fail,as[%s],group_id[%s]'%(rlt.message, group_id))
            return rlt
        old_user_list = []
        rm_list = []
        new_list = []
        for record in rlt.content:
            if record['user_id'] not in user_id_list:
                rm_list.append(record[ID])
            else:
                old_user_list.append(record['user_id'])
                
        for user_id in user_id_list:
            if user_id not in old_user_list:
                new_list.append(user_id)
        
        arr = []
        for user_id in new_list:
            arr.append({'user_id':user_id, 'group_id':group_id, 'join_time':NowMilli()})
        
        if len(arr):    
            ret = self.batch_insert(arr)
            if not ret.success:
                Log(1, 'update_relation.batch_insert fail,as[%s],group[%s]'%(ret.message, group_id))
        
        if len(rm_list):
            ret = self.remove({ID:{'$in':rm_list}})
            if not ret.success:
                Log(1, 'update_relation.remove fail,as[%s],group[%s]'%(ret.message, group_id))
                
        return Result({'delete':len(rm_list),'add':len(new_list)})
    
    def rm_relation_by_uid(self, user_id):
        rlt = self.remove({'user_id': user_id})
        if not rlt.success:
            Log(1, 'rm_relation_by_uid fail,as[%s]'%(rlt.message))
        return rlt

    def rm_relation_by_gid(self, group_id):
        rlt = self.remove({'group_id': group_id})
        if not rlt.success:
            Log(1, 'rm_relation_by_gid fail,as[%s]'%(rlt.message))
        return rlt
        