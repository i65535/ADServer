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
from mongodb.dbconst import MAIN_DB_NAME, EMAIL_TABLE


class EmailDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = EMAIL_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
        
    def update_email_list(self, classify, email_list):
        self.remove({'classify':classify})
        
        arr = []
        for email in email_list:
            email['classify'] = classify
            arr.append(email)
        
        if len(arr):
            return self.batch_insert(arr)
        else:
            return Result(0)
        


            
            
            
            
            
            
        