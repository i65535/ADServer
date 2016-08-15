# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年5月2日

@author: i65535
'''


from common.util import ParseNamespace
from frame.Logger import Log, WebLog
from mongodb.dbconst import AUTH_LOCAL, PERMISSION_ADMIN, PERMISSION_PUSH, \
    PERMISSION_PULL
from mongoimpl.registry.namespacedbimpl import NamespaceDBImpl
from mongoimpl.registry.userdbimpl import UserDBImpl
from mongoimpl.setting.configdbimpl import ConfigDBImpl


class AccessMgr(object):
    '''
    # 管理用户权限
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    def is_local_auth(self):
        return AUTH_LOCAL == ConfigDBImpl.instance().get_auth_method(AUTH_LOCAL)
    
    def allow_login(self, user_info):
        if user_info.get('source', AUTH_LOCAL) == AUTH_LOCAL:
            return True
        
        if self.is_local_auth():
            return False
        
        return True
        
    def verify_user_password(self, user_id, password, user_info):
        if user_info.get('source', AUTH_LOCAL) == AUTH_LOCAL:
            return password == user_info.get('password','')
        
        user_info['password'] = password
        return self.verify_user_info(user_info)
    
    def verify_user_info(self, user_info):
        if user_info.get('source', AUTH_LOCAL) == AUTH_LOCAL:
            return True
        
        WebLog(2, 'ldap server info invalid')
        return False
    
    def query_max_permission(self, user_id, res_name):
        npc = ParseNamespace(res_name)
        if not npc:
            Log(1, 'AccessMgr.query_access fail,as resource name[%s] is not contain a namespace'%(res_name))
            return 0
        
        if UserDBImpl.instance().is_admin(user_id):
            return 4
        
        if user_id == npc:
            return 4
        
        actions = self.query_access_level(user_id, npc)
        if PERMISSION_ADMIN in actions:
            return 4
        
        if PERMISSION_PUSH in actions:
            return 2
        
        if len(actions):
            return 1
        return 0
    
    def query_push_permission(self, user_id, res_name):
        permission = self.query_max_permission(user_id, res_name)
        return permission >= 2
    
    def query_admin_permission(self, user_id, res_name):
        permission = self.query_max_permission(user_id, res_name)
        return permission >= 4
    
    def query_pull_permission(self, user_id, res_name):
        permission = self.query_max_permission(user_id, res_name)
        return permission >= 1
    
    def query_ctrl_namespace(self, user_id, level=PERMISSION_PULL):
        rlt = UserDBImpl.instance().exec_db_script('useracl', user_id, level)
        if not rlt.success:
            Log(1, 'query_ctrl_namespace fail,as[%s]'%(rlt.message))
            return []
        
        rlt.content[user_id] = 4
        arr = []
        for npc, _ in rlt.content.iteritems():
            arr.append(npc)
                
        return arr
    
    def query_access(self, user_id, res_name):
        npc = ParseNamespace(res_name)
        if not npc:
            Log(1, 'AccessMgr.query_access fail,as resource name[%s] is not contain a namespace'%(res_name))
            return []
        
        if UserDBImpl.instance().is_admin(user_id):
            return ['*']
        
        if user_id == npc:
            return ['*']
        
        return self.query_nspc_access(user_id, npc)
    
    def query_access_level(self, user_id, namespace):
        rlt = UserDBImpl.instance().exec_db_script('access', user_id, namespace)
        if not rlt.success:
            Log(1, 'query_nspc_access fail,as[%s]'%(rlt.message))
            return []
        
        if not isinstance(rlt.content, list):
            return [] 
        
        if len(rlt.content) == 0:
            Log(1, '[%s]not access for[%s]'%(user_id, namespace))
            return []
        
        return rlt.content
    
    def query_nspc_access(self, user_id, namespace):
        levels = self.query_access_level(user_id, namespace)
        
        if PERMISSION_ADMIN in levels:
            return ['*']
        
        if PERMISSION_PUSH in levels:
            return ['push','pull']
        
        if PERMISSION_PULL in levels:
            return ['pull']  
        
    def query_guest_access(self, res_type, res_name):
        if 'repository' != res_type:
            Log(1, 'AccessMgr.query_guest_access for res[%s]'%(res_type))
            return []
        
        npc = ParseNamespace(res_name)
        if not npc:
            Log(1, 'AccessMgr.query_access fail,as resource name[%s] is not contain a namespace'%(res_name))
            return []
        
        if NamespaceDBImpl.instance().is_public_npc(npc):
            return ['pull']
        
        return []
    
    def accept_login(self, user_id, password):
        rlt =  UserDBImpl.instance().read_record(user_id)
        if not rlt.success:
            Log(1, 'accept_login[%s]fail,as get user info fail.'%(user_id))
            if self.is_local_auth():
                return False

            
        if self.allow_login(rlt.content):
            return self.verify_user_password(user_id, password, rlt.content)
        else:
            Log(1, 'user[%s]login fail, as[just support local user login.]'%(user_id))
            return False

    
            


    

