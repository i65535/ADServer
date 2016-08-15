# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement storage data manage
"""

import threading

from common.guard import LockGuard
from common.util import NowMilli
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, LOG_TABLE, ID


class LogDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = LOG_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def log(self, level, msg):
        self.create({'level':level, 'content':msg, 'time':NowMilli(), 'email':0, 'fail':0})
        
    def get_logs(self, level=None, from_time=None, to_time=None):
        query = {'email':0, 'fail':{'$lt':4}}
        if from_time is not None:
            query['time'] = {'$gt':from_time}
        if to_time is not None:
            query['time'] = {'$lt':to_time}
        if level is not None:
            query['level'] = level
            
        rlt = self.read_record_list(query)
        if rlt.success:
            return rlt.content
        return []

    def send_email_success(self, log_ids, to_addr):
        return self.find_and_modify_nums({ID:{'$in':log_ids}}, {'email':1})
        
    def send_email_fail(self, log_ids, to_addr):
        return self.find_and_modify_nums({ID:{'$in':log_ids}}, {"fail":1})
    
    def skip(self, log_ids):
        return self.updates({ID:{'$in':log_ids}}, {"fail":999})

            
        