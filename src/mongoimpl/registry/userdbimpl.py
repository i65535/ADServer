# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
实现用户信息相关的数据库操作
"""

import threading

from common.guard import LockGuard
from common.util import Result
from frame.Logger import Log, WebLog
from frame.errcode import INVALID_USER_INFO_ERR, USER_EXIST_ALREADY_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, ID, USER_TABLE


USER_RECORD_PREFIX = "USR"   # 订单记录ID的前缀

class UserDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = USER_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()

        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def create_user_record(self,user_info):
        if ID not in user_info:
            user_info[ID] = self.get_record_id(USER_RECORD_PREFIX)
        
        return self.insert(user_info)
    
        
    def update_user(self,_id, info):
        if ID in info:
            info.pop(ID)
        if 'role' in info and info['role'] not in ['ring0', 'ring5']:
            del info['role']
        if 'password' in info and not info['password']:
            del info['password']
        if 'join_time' in info:
            del info['join_time']
        
        return self.update({ID:_id}, info)

    def update_pwd(self,_id, pwd):
        return self.update({ID:_id}, {'password': pwd})
    
    def read_user_info(self,access_uuid):
        rlt = self.read_record_list({"access_uuid":access_uuid})
        if rlt.success and len(rlt.content):
            return rlt.content[0]
        else:
            return None
    
    def delete_user(self, user_id):
        WebLog(3, 'Admin deleted user [%s]'%(user_id))
        return self.remove({ID:user_id})
    
    def create_new_user(self, user_info):
        user_id = user_info.get(ID, None)
        if not user_id:
            return Result('', INVALID_USER_INFO_ERR, 'User info invalid.')

        if self.is_exist({ID:user_id}):
            return Result('', USER_EXIST_ALREADY_ERR, 'User exist already.')
        
        if 'role' not in user_info or user_info['role'] not in ['ring0', 'ring5']:
            user_info['role'] = 'ring5'
            
        rlt = self.insert(user_info)
        if not rlt.success:
            Log(1, 'create_new_user fail,as[%s]'%(rlt.message))
        WebLog(3, 'Admin created new user [%s]'%(user_id))
        return rlt
            
    def is_admin(self, user_id):
        return self.is_exist({ID:user_id, 'role':'ring0'})
           
     
    def accept_disclaimer(self, user_id):
        WebLog(3, 'User[%s]accept disclaimer.'%(user_id))
        rlt = self.update({ID:user_id}, {'agreement':True})
        if not rlt.success:
            Log(1, 'accept_disclaimer update fail,as[%s],user[%s]'%(rlt.message, user_id))
        return rlt
        
        
    def get_password(self, user_id):
        rlt = self.read_record(user_id, projection=['password'])
        if not rlt.success:
            Log(1, 'get_password fail, the user[%s] not exist'%(user_id))
            return ''
             
        return rlt.content.get('password', '')
        
        
    