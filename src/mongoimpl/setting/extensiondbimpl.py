# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement Order data manage
"""

import threading

from common.guard import LockGuard
from common.util import Result
from frame.Logger import Log
from frame.errcode import INVALID_EXTENSION_INFO_ERR, \
    EXTENSION_ADDRESS_EXIST_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, EXTENSTION_TABLE, ID


class ExtensionDBImpl(DBBase):
    
    db = MAIN_DB_NAME
    collection = EXTENSTION_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
            
    def delete_extension(self, user_id, ext_id):
        rlt = self.remove({ID:ext_id, 'owner':user_id})
        if not rlt.success:
            Log(1, 'delete_extension fail,as[%s]'%(rlt.message))
        return rlt
                  
    def update_extension(self, ext_id, ext_info):
        if ID in ext_info:
            del ext_info[ID]
            
        if 'address' not in ext_info:
            return Result('address', INVALID_EXTENSION_INFO_ERR, 'address is must')
        
        if self.is_exist({ID:{'$ne':ext_id}, 'address':ext_info['address'], 'owner':ext_info['owner']}):
            return Result(ext_info['address'], EXTENSION_ADDRESS_EXIST_ERR, 'the address is exist already')
        
        rlt = self.update({ID:ext_id}, ext_info)
        if not rlt.success:
            Log(1, 'update_extension[%s]fail,as[%s]'%(ext_id, rlt.message))
        return rlt
    
    def create_extension(self, ext_info):
        if 'address' not in ext_info:
            return Result('address', INVALID_EXTENSION_INFO_ERR, 'address is must')
        
        if self.is_exist({'address':ext_info['address'], 'owner':ext_info['owner']}):
            return Result(ext_info['address'], EXTENSION_ADDRESS_EXIST_ERR, 'the address is exist already')
        
        return self.create(ext_info)
    
    def get_extension_info(self, user_id, ext_id):
        return self.read_record_data({ID:ext_id, 'owner':user_id})
        
        
    def get_extension_list(self, query=None):
        return self.read_record_list(query)
        