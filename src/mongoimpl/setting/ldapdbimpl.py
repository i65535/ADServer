# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement storage data manage
"""

import threading

from common.guard import LockGuard
from common.util import Result
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, ID, LDAP_TABLE


class LDAPDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = LDAP_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
        
    def default_ldap(self):
        rlt = self.read_record_list()
        if rlt.success and len(rlt.content):
            return Result(rlt.content[0])

        return Result({})
            
    def update_ldap_info(self, ldap_info):
        _id = ldap_info.pop(ID, 1)
        return self.update({ID:_id}, ldap_info, True)
    
    def default_ldap_info(self):
        rlt = self.read_record_list()
        if rlt.success and len(rlt.content):
            return rlt.content[0]

        return {}
             
            
            
            
            
            
            
        