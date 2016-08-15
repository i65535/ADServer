# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
from common.guard import LockGuard
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, CONFIG_TABLE, ID
import threading

"""
"""

AUTHORIZE = "authorize"
STORAGE_TYPE = 'storage_type'
GENERALSETTING = "generalsetting"
VERSION = "version"

class ConfigDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = CONFIG_TABLE
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
        
    def save_config(self,config):
        try:
            _id = config.pop(ID)
        except Exception:
            return self.create(config)
        else:
            return self.update({ID:_id},config)
        
    def get_auth_method(self, default=''):
        return self.get_value(AUTHORIZE, default)
    
    def set_auth_method(self, method):
        return self.update_value(AUTHORIZE, method)
    
    def get_storage_type(self, default=''):
        return self.get_value(STORAGE_TYPE, default)
    
    def set_storage_type(self, storage_type):
        return self.update_value(STORAGE_TYPE, storage_type)

    def get_general_info(self):
        return self.read_record(GENERALSETTING)
    
    def set_general_info(self, info):
        # info.pop(ID, '')
        return self.update({ID:GENERALSETTING}, info, True)
    
    def get_version(self):
        return self.get_value(VERSION)
    
    def set_version(self, version):
        return self.update_value(VERSION, version)

    def get_value(self, identy, default_value=''):
        rlt = self.read_record(identy)
        if rlt.success:
            return rlt.content['value']
        return default_value
        
    
    def update_value(self, identy, value):
        rlt = self.update({ID:identy}, {'value':value}, True)
        if not rlt.success:
            Log(1, 'update_value[%s][%s]fail,as[%s]'%(identy, value, rlt.message))
        return rlt
        

            
            
            
            
            
            
            
            
            
            
            
        