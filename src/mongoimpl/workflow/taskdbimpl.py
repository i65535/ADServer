# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 The i65535.
# See LICENSE for details.

"""
实现任务相关的数据库操作
"""

import threading

from common.guard import LockGuard
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, TASK_TABLE


SUCCESS = 0
FAIL    = 1
PROCESSING = 2
ROLLBACK = 3
WAITING = 4
INITIAL = 100
    

class TaskDBImpl(DBBase):
    
    db = MAIN_DB_NAME
    collection = TASK_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()

        return cls._instance
    
    def __init__(self):
        super(TaskDBImpl, self).__init__(self.db, self.collection)
        
    def update_to_db(self, task_id, taskObj):
        if "_id" in taskObj:
            del taskObj["_id"]
        return self.update({"_id":task_id}, taskObj)
    
    def create_task(self, taskObj):
        return self.create(taskObj)
    
    def read_task_page(self):
        return self.read_record_list()
    
    def read_interrupt_task_list(self, task_type_list=None):
        query = {"__state":{"$nin":[0,1]}}
        if task_type_list:
            if isinstance(task_type_list,list):
                query["task_type"] = {"$in":task_type_list}
            else:
                query["task_type"] = task_type_list
        
        return self.read_record_list(query)
    
    def read_after_pay_task_list(self, task_type_list):
        """
        # 要返回所有没有成功的任务
        """
        query = {"__state":{"$ne":0}}
        if isinstance(task_type_list,list):
            query["task_type"] = {"$in":task_type_list}
        else:
            query["task_type"] = task_type_list
        
        return self.read_record_list(query)
        
     
