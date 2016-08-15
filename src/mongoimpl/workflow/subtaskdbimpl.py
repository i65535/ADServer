# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 The i65535.
# See LICENSE for details.

"""
实现子任务相关的数据库操作
子任务是指那些组成一个任务计划的原子操作。
"""

import threading

from common.guard import LockGuard
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, SUB_TASK_TABLE, ID



class SubTaskDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = SUB_TASK_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()

        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def update_to_db(self,task_id,taskObj):
        if ID in taskObj:
            del taskObj[ID]
        return self.update({ID:task_id}, taskObj)
    
    def read_task_list(self,parent_task_id):
        return self.read_record_list({"parent_task_id":parent_task_id})
    
    def read_task_by_ids(self,task_id_list):
        return self.read_record_list({ID:{"$in":task_id_list}})
    
    def read_sub_task_info(self,task_id):
        return self.read_record(task_id)
    
    def create_task(self,task_id,taskObj):
        taskObj["_id"] = task_id
        taskObj["progress"] = 0
        return self.insert(taskObj)
     
