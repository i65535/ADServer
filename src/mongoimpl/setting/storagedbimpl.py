# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement storage data manage
"""

import threading

from common.guard import LockGuard
from common.util import Result
from frame.Logger import WebLog
from frame.errcode import INVALID_STORAGE_TYPE_ERR, \
    INVALID_STORAGE_PATH_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, STORAGE_TABLE, ID, LOCAL_FILE_SYSTEM, \
    GLUSTERFS


SUPPORT_STORE_TYPE = [LOCAL_FILE_SYSTEM, GLUSTERFS]

class StorageDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = STORAGE_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
        
    def all_storage_type(self):
        rlt = self.read_record_list()
        if not rlt.success:
            WebLog(1, 'Storage.read_record_list fail,as[%s]'%(rlt.message))
        
        return rlt
        
    def update_store(self, store):
        _type = store.pop(ID,'')
        if _type not in SUPPORT_STORE_TYPE:
            WebLog(2, 'invalid storage type[%s]'%(_type))
            return Result(_type, INVALID_STORAGE_TYPE_ERR, 'invalid storage type')
        
        if str(store.get('path','')).strip() == '':
            WebLog(2, 'storage path can not be empty')
            return Result(_type, INVALID_STORAGE_PATH_ERR, 'invalid storage path')
        
        rlt = self.update({ID:_type}, store, True)
        if not rlt.success:
            WebLog(2, 'update storage[%s] info fail.'%(_type))
            return rlt
        
        return Result(_type)
            
            
            
            
            
            
            
            
            
        