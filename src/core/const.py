# -*- coding: utf-8 -*-


class ScheduStatus(object):
    """计划任务的状态"""
    ENABLE = 1     #
    DISABLE = 0    # 
    TERMINATE = -1 # 对应已删除状态
    
class ScheduleType():
    WEEK = "w"
    MONTH = "m"
    INTERVAL = "i"
    
class TaskStatus(object):
    SUCCESS    = "success"  
    FAIL       = "fail"
    CANCEL     = "cancel"
    PROCESSING = "processing" 
    WAITING    = "waiting"
