# -*- coding: utf-8 -*-
# Copyright (c) 2007-2012 The i65535.
# See LICENSE for details.
"""
实现定时任务的管理
"""

import json
import threading
import time

from common.guard import LockGuard
from common.util import Result, ConvertToDatetime
from core.const import ScheduleType
from frame.Logger import Log
from frame.authen import ring0
from frame.errcode import INVALID_JSON_DATA_ERR
from frame.schedulemgr import ScheduledMgr
from mongoimpl.setting.scheduledbimpl import ScheduleDBImpl, ScheduleJobDBImpl
from schedule.schedulejob import ScheduleJob


class Actor(object):
    __lock = threading.Lock()
    
    @classmethod
    def instance(cls):
        '''
        Limits application to single instance
        '''
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        ScheduledMgr.instance()

        self.check_system_schedu_job()
        
    def check_system_schedu_job(self):
        count = ScheduleJobDBImpl.instance().job_number()
        Log(3,"check_system_schedu_job [%s] job in schedule."%(count))
        
        if count > 0:
            return
        
        rlt = ScheduleDBImpl.instance().get_schedule_info('clean')
        if rlt.success:
            if rlt.content.get('status', 0) == 1:
                job = CleanJob(rlt.content)
                return job.start()
    
    @ring0
    def update_cleanschedule(self, post_data):
        try:
            info = json.loads(post_data.replace("'", '"'))
            info['interval'] = int(info.get('interval', 0))
            start_date = info.get("start_date",None)
            if start_date:
                ConvertToDatetime(start_date)
        except Exception,e:
            Log(1,"update_cleanschedule parameter is invalid,input[%s]"%(post_data))
            return Result('', INVALID_JSON_DATA_ERR, str(e))
        
        rlt = ScheduleDBImpl.instance().get_schedule_info('clean')
        if rlt.success:
            schedule = rlt.content
            schedule.update(info)
            job = CleanJob(schedule)
            return job.update_job_info()
        else:
            job = CleanJob(info)
            return job.save_and_start()
            
    
    @ring0
    def cleanschedule(self):
        rlt = ScheduleDBImpl.instance().get_schedule_info('clean')
        if not rlt.success:
            return Result({'interval':86400, 'status':0,'mode':'i','start_date':time.strftime("%Y-%m-%d 00:00:00",time.localtime())})
        
        return rlt
            
        
def garbage_collect():
    Log(3, 'garbage_collect begin')



CLEAN_SCHEDULE = "clean"


class CleanJob(ScheduleJob):
    def __init__(self, schedule):
        self.mode = ''
        self.interval = 99999
        self.exec_time = ''
        self.days = ''
        
        super(CleanJob, self).__init__(schedule)
        self.job_type = CLEAN_SCHEDULE
        self.end_time = "always"
        self.cron_time = self.parse_time_parameter(schedule)
        self.start_date = self.cron_time['start_date']
        
    def parse_time_parameter(self, schedule):
        if self.mode == ScheduleType.INTERVAL:
            return self.parse_interval_time(schedule)
        else:
            return self.parse_cron_time(schedule)
        
    def snapshot(self):
        snap = super(CleanJob, self).snapshot()
        snap['mode'] = self.mode
        snap['start_date'] = self.start_date
        snap['exec_time'] = self.exec_time
        
        if self.mode == ScheduleType.INTERVAL:
            snap['interval'] = self.interval
        else:
            snap['exec_time'] = self.exec_time
            snap['days'] = self.days
        
        return snap
        
    def start(self):
        if self.mode in [ScheduleType.WEEK, ScheduleType.MONTH]:
            return self.create_cron_job(garbage_collect)
        else:
            return self.create_interval_job(garbage_collect)

