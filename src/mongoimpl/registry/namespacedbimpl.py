# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""


import threading

from common.guard import LockGuard
from common.util import NowMilli, Result, ParseNamespace
from frame.Logger import Log, WebLog
from frame.errcode import INVALID_NAMESPACE_INFO_ERR, NAMESPACE_EXIST_ALREADY_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, NAMESPACE_TABLE, ID, PERMISSION_PUBLIC, \
    NAMESPACE_TYPE_ORGANIZATION
from mongoimpl.registry.groupnamespcdbimpl import GroupNamespcDBImpl


class NamespaceDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = NAMESPACE_TABLE
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
        
    def save_namespace(self, namespace, user_id):
        rlt = self.count({ID:namespace})
        if rlt.success and rlt.content > 0:
            Log(1, 'save_namespace The name space exist. namespace[%s]'%(namespace))
            return rlt
        
        t = NowMilli()
        data = {ID:namespace,'create_time':t,'update_time':t, 'owner_id':user_id, 'desc':'','permission':PERMISSION_PUBLIC, 'type':NAMESPACE_TYPE_ORGANIZATION}
        ret = self.insert(data)
        if not ret.success:
            Log(1, 'save namespace[%s] fail,as[%s]'%(namespace, rlt.message))
        return ret
    
    def create_new_nspc(self, info):
        namespace = info.get(ID, None)
        if not namespace:
            return Result('', INVALID_NAMESPACE_INFO_ERR, 'Namespace info invalid.')

        if self.is_exist({ID:namespace}):
            return Result('', NAMESPACE_EXIST_ALREADY_ERR, 'Namespace exist already.')
        
        groups = info.pop('groups', [])
        info['create_time'] = NowMilli()
        info['update_time'] = NowMilli()
        rlt = self.insert(info)
        if not rlt.success:
            Log(1, 'create_new_nspc fail,as[%s]'%(rlt.message))
            return rlt
        
        WebLog(3, 'Admin created the project [%s]'%(namespace))
        
        if groups:
            return GroupNamespcDBImpl.instance().create_relation(namespace, groups)
        return Result('')
        
    def update_namespace(self, _id, info):
        info.pop(ID, None)
        
        info['update_time'] = NowMilli()
        groups = info.pop('groups', None)
        rlt = self.update({ID:_id}, info)
        if not rlt.success:
            Log(1, 'create_new_nspc fail,as[%s]'%(rlt.message))
            return rlt
        
        WebLog(3, 'Admin edited the project [%s]'%(_id))
        
        if isinstance(groups, list):
            return GroupNamespcDBImpl.instance().update_relation(_id, groups)
        
        return rlt
            
    def delete_namespace(self, namespace):
        return self.remove({ID:namespace}) 
    
    
    def upsert_namespace(self, repositories):
        if len(repositories) == 0:
            return
        
        rlt = self.read_record_list(projection=[])
        if not rlt.success:
            Log(1, 'upsert_namespace.read_record_list fail,as[%s]'%(rlt.message))
            return rlt
        
        local_npc = []
        for record in rlt.content:
            local_npc.append(record[ID])
        
        namespaces = []
        new_npc = []
        for repo in repositories:
            npc = ParseNamespace(repo)
            if not npc:
                continue
            
            if npc not in local_npc:
                if npc in new_npc:
                    continue
                new_npc.append(npc)
                namespaces.append({ID:npc, 'create_time':NowMilli(), 'permission':'public', 'owner_id':'', 'desc':'', 'type':NAMESPACE_TYPE_ORGANIZATION})

        if len(namespaces) > 0:
            rlt = self.batch_insert(namespaces)
            if rlt.success:
                Log(3, 'upsert_repository insert [%s] new record'%(rlt.content) )
            else:
                Log(1, 'upsert_repository insert record fail,as[%s]'%(rlt.message) )
                
        return Result(len(namespaces))


    def is_public_npc(self, namespace):
        return self.is_exist({ID:namespace, 'permission':'public'})
            
            
            
            
            
            
            
            
            
            
        