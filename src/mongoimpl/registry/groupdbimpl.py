# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import Result
from frame.Logger import Log, WebLog
from frame.errcode import GROUP_EXIST_ALREADY_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, GROUP_TABLE, ID
from mongoimpl.registry.usergroupdbimpl import UserGroupDBImpl


GROUP_RECORD_PREFIX = 'GRP'

class GroupDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = GROUP_TABLE
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
        self.__store = {}
        
    def load_group_data(self):
        rlt = self.read_record_list()
        if not rlt.success:
            return rlt
        
        for info in rlt.content:
            self.__store[info[ID]] = info.get('group_name','unknown name')

        
    def create_group_record(self, group_info):
        if ID not in group_info:
            group_info[ID] = self.get_record_id(GROUP_RECORD_PREFIX)
        
        return self.insert(group_info)
    
        
    def update_group(self, _id, group_info):
        group_name = group_info.get('group_name', None)

        if self.is_exist({'group_name':group_name,ID:{'$ne':_id}}):
            return Result('', GROUP_EXIST_ALREADY_ERR, 'Group exist already.')
        
        user_ids = group_info.pop('userids','')
        rlt = self.update({ID:_id}, group_info)
        if not rlt.success:
            Log(1, 'update_group fail,as[%s]'%(rlt.message))
            return rlt
        
        WebLog(3, 'Admin edited usergroup [%s]'%(group_name))
        
        if user_ids:
            arr = user_ids.split('#')
            return UserGroupDBImpl.instance().update_relation(_id, arr)
        else:
            UserGroupDBImpl.instance().rm_relation_by_gid(_id)
        return rlt

            
    def create_new_group(self, group_info):
        group_name = group_info.get('group_name', None)

        if self.is_exist({'group_name':group_name}):
            return Result('', GROUP_EXIST_ALREADY_ERR, 'Group exist already.')
        
        user_ids = group_info.pop('userids','')
        
        rlt = self.create(group_info)
        if not rlt.success:
            Log(1, 'create_new_group fail,as[%s]'%(rlt.message))
            return rlt
        
        WebLog(3, 'Admin created usergroup [%s]'%(group_name))
            
        if user_ids:
            arr = user_ids.split('#')
            return UserGroupDBImpl.instance().create_relation(group_info[ID], arr)
        else:
            return rlt

    def delete_group(self, group_id):
        rlt = self.read_record(group_id)
        if rlt.success:
            WebLog(3, 'Admin delete usergroup [%s]'%(rlt.content['group_name']))
            
            return self.remove({ID:group_id})
        else:
            Log(1, 'delete_group [%s] fail.'%(group_id))
            return rlt
            
    def get_group_name(self, group_id):
        try:
            group_id = int(group_id)
        except:
            return 'unknown name'  
        
        if group_id not in self.__store:
            self.load_group_data()
            
        return self.__store.get(group_id, 'unknown name')
        
        
                  
        