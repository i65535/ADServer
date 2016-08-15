# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 The i65535.
# See LICENSE for details.




import threading
import time

from common.guard import LockGuard
from common.util import NowMilli
from core.const import TaskStatus
from frame.Logger import Log
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, ID, OPERATE_TABLE


"""
实现操作信息管理
"""

class OperateDBImpl(DBBase):
    
    db = MAIN_DB_NAME
    collection = OPERATE_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def create_operate_log(self, instance_id, operate_info):
        record = operate_info
        record["instance_id"] = instance_id                                    
        record["content"] = {}                                   # 操作结果信息
        record["state"] = TaskStatus.PROCESSING                  # 操作状态
        record["error_code"] = 0                                 # 操作错误码
        record["remark"] = ""                                    # 操作备注信息
        
        record["create_time"] = time.time() * 1000               # 操作创建时间
        record["launch_time"] = -1                               # 操作启动时间
        record["finish_time"] = -1                               # 操作结束时间
        
        return self.create(record)
    
    def create_operate_fail_log(self,instance_id,operate_info):
        record = operate_info
        record["instance_id"] = instance_id                                    
        record["content"] = {}                                   # 操作结果信息
        record["state"] = TaskStatus.FAIL                        # 操作状态
        
        t = time.time() * 1000
        record["create_time"] = t                                # 操作创建时间
        record["launch_time"] = t                                # 操作启动时间
        record["finish_time"] = t                                # 操作结束时间
        record["cost_time"] = 0                                  # 操作结束时间
        
        return self.create(record)
    
    def read_by_task_id(self,task_id):
        return self.read_record(task_id)
    
    def get_create_time(self,operate_id):
        create_time = -1
        rlt = self.read_record(operate_id,fields=["create_time"])
        if not rlt.success:
            Log(1,"OperateDBImpl.begin_process,the operate not exist[%s]"%(operate_id))
            return rlt
        else:
            create_time = rlt.content.get("create_time")
            
        return create_time
    
    def update_operate_info(self,task_id,task_info):
        self.update({ID:task_id}, task_info)
        
    def begin_process(self,order_id):
        create_time = self.get_create_time(order_id)
            
        t = NowMilli()
        wait_time = t - create_time
        return self.update({ID:order_id},{
                                          "wait_time":wait_time,
                                          "launch_time":t,
                                          "state":TaskStatus.PROCESSING})
        
    def set_success(self,order_id,task_result=None,msg=None):
        create_time = self.get_create_time(order_id)
        
        taskObj = {}
        taskObj["state"] = TaskStatus.SUCCESS
        taskObj["finish_time"] = NowMilli()
        taskObj["cost_time"] = NowMilli() - create_time
        
        if msg:
            taskObj["remark"] = msg
        if task_result:
            taskObj["content"] = task_result
        
        return self.update({ID:order_id}, taskObj)
    
    def set_fail(self,order_id,reason,err_code):
        create_time = self.get_create_time(order_id)
        taskObj = {}
        taskObj["remark"] = reason
        taskObj["state"] = TaskStatus.FAIL
        taskObj["finish_time"] = NowMilli()
        taskObj["cost_time"] = NowMilli() - create_time
        taskObj["error_code"] = err_code
        return self.update({ID:order_id}, taskObj)
        

        
    

    
    
        