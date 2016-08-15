# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli, Result
from frame.Logger import Log, WebLog
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, GROUP_NAMESPACE_TABLE, PERMISSION_ADMIN, PERMISSION_PUSH, \
    PERMISSION_PULL
from mongoimpl.registry.groupdbimpl import GroupDBImpl


ACTIONS = {str(PERMISSION_ADMIN):'ADMIN', str(PERMISSION_PUSH):'PUSH', str(PERMISSION_PULL):'PULL'}

class GroupNamespcDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = GROUP_NAMESPACE_TABLE
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
        
    def create_relation(self, namespace, group_list):
        groupmgr = GroupDBImpl.instance()
        self.log_new_rel(groupmgr, namespace, group_list)
        return self._create_relation(namespace, group_list)
        
        
    def _create_relation(self, namespace, group_list):
        arr = []
        for group in group_list:
            try:
                group_id = int(group['group_id'])
                control = int(group['control'])
            except:
                Log(1, 'GroupNamespcDBImpl create_relation except,the group_id[%s] invalid'%(group['group_id']))
            arr.append({'namespace':namespace, 'group_id':group_id, 'control':control, 'join_time':NowMilli()})
            
        if arr:    
            return self.batch_insert(arr)
        return Result(namespace)
    
    
    def update_relation(self, namespace, group_list):
        self.parse_change(namespace, group_list)
        self.remove({'namespace':namespace})
        if group_list:
            return self._create_relation(namespace, group_list)
        
        return Result(namespace)

    def rm_relation_by_nid(self, namespace_id):
        rlt = self.remove({'namespace_id': namespace_id})
        if not rlt.success:
            Log(1, 'rm_relation_by_nid fail,as[%s]'%(rlt.message))
        return rlt

    def rm_relation_by_gid(self, group_id):
        rlt = self.remove({'group_id': group_id})
        if not rlt.success:
            Log(1, 'rm_relation_by_gid fail,as[%s]'%(rlt.message))
        return rlt
            
            
    def parse_change(self, namespace, group_list):
        rlt = self.read_record_list({'namespace':namespace})
        if not rlt.success:
            Log(1, 'parse_change.read_record_list fail,as [%s]'%(rlt.message))
            return rlt
        
        old = {}
        old_rel = []
        for rel in rlt.content:
            old[str(rel['group_id'])] = rel['control']
            old_rel.append('%s:%s'%(rel['group_id'], rel['control']))
        
        delete = []
        update = []
        new =[]
        new_groups = [] 
        for ng in group_list:
            if 'group_id' not in ng or 'control' not in ng:
                continue
            
            if str(ng['group_id']) in old.keys():
                key = '%s:%s'%(ng['group_id'], ng['control'])
                if key not in old_rel:
                    ng['old_control'] = old.get(str(ng['group_id']))
                    update.append(ng)
            else:
                new.append(ng)
            
            new_groups.append(str(ng['group_id']))
            
        for o_gid in old.keys():
            if o_gid not in new_groups:
                delete.append(int(o_gid))
                
        groupmgr = GroupDBImpl.instance()
        if len(new):
            self.log_new_rel(groupmgr, namespace, new)
        
        if len(update):
            self.log_update_rel(groupmgr, namespace, update)
            
        if len(delete):
            self.log_delete_rel(groupmgr, namespace, delete)
                
        
    def log_new_rel(self, groupmgr, namespace, rel_list):
        for rel in rel_list:
            WebLog(3, 'Admin added user group [%s] with role %s to the project [%s]'%(
                                    groupmgr.get_group_name(rel['group_id']), 
                                    ACTIONS.get(str(rel['control']), 'unknown'), 
                                    namespace))
    
    def log_update_rel(self, groupmgr, namespace, rel_list):
        for rel in rel_list:
            WebLog(3, 'Admin changed the role of user group [%s] from %s to %s within the project [%s]'%(
                                    groupmgr.get_group_name(rel['group_id']), 
                                    ACTIONS.get(str(rel['old_control']), 'unknown'), 
                                    ACTIONS.get(str(rel['control']), 'unknown'), 
                                    namespace))
            
    def log_delete_rel(self, groupmgr, namespace, group_list):
        for group_id in group_list:
            WebLog(3, 'Admin removed user group [%s] from the project [%s]'%(
                                    groupmgr.get_group_name(group_id), 
                                    namespace))
            
            
                
            
        