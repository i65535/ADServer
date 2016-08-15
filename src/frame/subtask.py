# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 The i65535.
# See LICENSE for details.


"""
这个类主要功能：
1、实现任务信息分拣，恢复，
2、实现通用数据操作
"""

import time

from frame.Logger import Log
from frame.task import Task
from mongoimpl.workflow.subtaskdbimpl import SubTaskDBImpl


LOGIN_TO_REMOTE_REGISTRY_TASK_SUFFIX = 'REMOTE_LOGIN'
LOGIN_TO_REMOTE_REGISTRY_TASK = 'remote_login'
LOGIN_TO_REMOTE_REGISTRY_INDEX = 100

PULL_IMAGE_TASK_SUFFIX = 'PULL'
PULL_IMAGE_TASK = 'pull'
PULL_IMAGE_INDEX = 200

LOGIN_TO_LOCAL_REGISTRY_TASK_SUFFIX = 'LOCAL_LOGIN'
LOGIN_TO_LOCAL_REGISTRY_TASK = 'local_login'
LOGIN_TO_LOCAL_REGISTRY_INDEX = 300

TAG_IMAGE_TASK_SUFFIX = 'TAG'
TAG_IMAGE_TASK = 'tag'
TAG_IMAGE_INDEX = 400

PUSH_IMAGE_TASK_SUFFIX = 'PUSH'
PUSH_IMAGE_TASK = 'push'
PUSH_IMAGE_INDEX = 500




class SubTask(Task):
    def __init__(self,task_info,suffix):
        parent_task_id = task_info.get("parent_task_id", "")
        _id = '%s%s'%(parent_task_id, suffix)
        info = {}
        self.message = ''
        self.task_type = None
        self.weight = 1
        self.progress = 0
        if _id in task_info:
            info = task_info[_id]
        else:
            info["_id"] = _id
            info["parent_task_id"] = parent_task_id

        super(SubTask, self).__init__(info)
        
    def pre_work(self):
        self.save_to_db()
        
    def snapshot(self):
        snap = super(SubTask, self).snapshot()
        snap["_id"] = self._id
        snap["parent_task_id"] = self.parent_task_id
        snap["task_type"] = self.task_type
        snap["progress"] = self.progress
        
        return snap
    
    def save_to_db(self):
        taskObj = self.snapshot()
        
        rlt = SubTaskDBImpl.instance().create_task(self._id,taskObj)
        if not rlt.success:
            Log(1,"SubTask.save_to_db[%s] fail,as[%s]"%(self._id,rlt.message))
            
    def update(self,taskObj=None):
        if taskObj is None:
            taskObj = self.snapshot()
        rlt = SubTaskDBImpl.instance().update_to_db(self._id,taskObj)
        if not rlt.success:
            Log(1,"SubTask.update[%s] fail,as[%s]"%(self._id,rlt.message))
            
    def end_work(self,task_rlt):
        self.progress = 100
        snap = super(SubTask, self).snapshot()
        snap["progress"] = 100
        snap["cost_time"] = time.time() * 1000 - snap.get("create_time",0)
        snap["finish_time"] = time.time() * 1000
        self.update(snap)
        
    def get_progress(self):
        return self.weight * self.progress
    
    def add_progress(self, step=1):
        self.progress += step
        self.progress = 99 if self.progress > 99 else self.progress

    
    
    
    
    
    
    
    
    
        
            
            