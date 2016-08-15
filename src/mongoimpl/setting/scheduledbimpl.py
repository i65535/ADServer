# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
Implement schedule data manage
"""

import threading

from common.guard import LockGuard
from core.const import ScheduStatus
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, SCHEDULE_TABLE, ID, SCHEDULE_JOB_TABLE


class ScheduleDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = SCHEDULE_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
    
    def get_schedule_info(self, job_type):
        return self.read_record_data({'job_type':job_type}, projection=['mode', 'exec_time', 'days', 'interval', 'start_date', 'status'])
    
    def get_schedule_info_by_id(self, schedule_id):
        return self.read_record_data(schedule_id, projection=['mode', 'exec_time', 'days', 'interval', 'start_date', 'status'])
    
    def create_schedule_job(self, job_info):
        return self.create(job_info)
    
    def update_schedule_job(self, job_id, job_info):
        return self.update({ID:job_id}, job_info)
    
    def remove_schedule(self, job_id):
        rlt = self.updates({ID:job_id}, {"status":ScheduStatus.TERMINATE})
        if not rlt.success:
            Log(1,"remove_schedule[%s] fail,as[%s]"%(job_id,rlt.message))
            
        return rlt
        

class ScheduleJobDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = SCHEDULE_JOB_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def job_number(self):
        rlt = self.count({})
        if rlt.success :
            return rlt.content
        
        return 0
        

            
            
            
            
            
            
        