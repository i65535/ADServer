# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
实现VM相关的数据库操作
"""

import threading

from common.guard import LockGuard
from common.util import Result
from frame.Logger import Log
from frame.errcode import WORK_INFO_INVALID_ERR
from mongodb.dbbase import DBBase
from mongodb.dbconst import MAIN_DB_NAME, ID, WORK_DATA_TABLE


class WorkDBImpl(DBBase):
    db = MAIN_DB_NAME
    collection = WORK_DATA_TABLE
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()

        return cls._instance
    
    def __init__(self):
        DBBase.__init__(self, self.db, self.collection)
        
    def create_work_record(self, work_info):
        return self.create(work_info)
    
    def update_all_work_info(self, work_id, work_info):
        """
        # work 结构信息非常多，这个方法实现替换功能，不做部分字段的修改
        """
        if work_id:
            return self.replace({ID:work_id}, work_info)
        else:
            Log(1, "update_all_work_info fail,as[no work id]")
            return Result("", WORK_INFO_INVALID_ERR, "update_all_work_info fail,as[no work id]")
        
    def update_work_part_info(self, _id, work_info):
        return self.update({ID:_id}, work_info)
    
    def read_work_info(self, work_id):
        return self.read_record(work_id)

        
        
        
        
    