# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
这是一个基类，用于维护一个调度任务的信息，
包括，入库存储，更新
"""

from datetime import datetime

from common.util import ConvertToDatetime, Result
from core.const import ScheduStatus, ScheduleType
from frame.Logger import Log, PrintStack
from frame.errcode import CREATE_CRON_SCHEDULE_FAIL, \
    CREATE_INTERVAL_SCHEDULE_FAIL
from frame.schedulemgr import ScheduledMgr
from mongoimpl.setting.scheduledbimpl import ScheduleDBImpl


DEFAULT_TIMEZONE = "Asia/Shanghai"


class ScheduleJob(object):
    def __init__(self,job_info):
        """
        job_info = {'cron_time':{}}
        """
        self.scheduMgr = ScheduledMgr.instance()
        self.end_time = None
        self.status = ScheduStatus.ENABLE
        self.cron_time = {}
        self._id = ""
        self.args = []
        self.kwargs = {}
        self.job_type = ""
        self.mode = ""
        self.__dict__.update(job_info)
        
    def snapshot(self):
        return {
            "end_time":self.end_time,
            "cron_time":self.cron_time,
            "job_type":self.job_type,
            "args":self.args,
            "kwargs":self.kwargs,
            "status":self.status
        }

    
    def update_job_info(self):
        self.scheduMgr.remove_job(str(self._id))
        job_info = self.snapshot()
        rlt = self.update_to_db(job_info)
        if rlt.success and self.status == ScheduStatus.ENABLE:
            return self.start()
        return rlt
    
    def is_expire(self):
        return False
    
    def save_and_start(self):
        rlt = self.save_to_db()
        if rlt.success and self.status == ScheduStatus.ENABLE:
            return self.start()
        else:
            Log(1,"ScheduleJob.save_and_start fail,as[%s]"%(rlt.message))
            return rlt
        
    def start(self):
        pass
    
    def terminate(self):
        self.scheduMgr.remove_job(str(self._id))
        self.status = ScheduStatus.TERMINATE
        self.update_to_db({"status":ScheduStatus.TERMINATE})
    
    def stop(self):
        Log(3,"Job[%s]stop"%(self._id))
        self.scheduMgr.remove_job(str(self._id))
        self.status = ScheduStatus.DISABLE
        self.update_to_db({"status":ScheduStatus.DISABLE})
    
    def save_to_db(self):
        job_info = self.snapshot()
        rlt = ScheduleDBImpl.instance().create_schedule_job(job_info)
        if not rlt.success:
            Log(1,"ScheduleJob.save_to_db fail.as[%s]"%(rlt.message))
        else:
            self._id = rlt.content
        
        return rlt
    
    def update_to_db(self, job_info):
        rlt = ScheduleDBImpl.instance().update_schedule_job(self._id, job_info)
        if not rlt.success:
            Log(1,"ScheduleJob.update_to_db fail.as[%s]"%(rlt.message))
        return rlt
    
    def create_cron_job(self,func):
        job_cfg = {'id':str(self._id)}
        job_cfg.update(self.cron_time)
        try:
            self.scheduMgr.add_cron_job(func,job_cfg,*self.args,**self.kwargs)
        except Exception,e:
            PrintStack()
            Log(1,"ScheduleJob.create_interval_job fail.as[%s]"%(str(e)))
            return Result('', CREATE_CRON_SCHEDULE_FAIL, 'add_cron_job fail')
        else:
            return Result('ok')
    
    def create_interval_job(self,func):
        job_cfg = {'id': str(self._id)}
        job_cfg.update(self.cron_time)
        try:
            self.scheduMgr.add_interval_job(func,job_cfg,*self.args,**self.kwargs)
        except Exception,e:
            PrintStack()
            Log(1,"ScheduleJob.create_interval_job fail.as[%s]"%(str(e)))
            return Result('', CREATE_INTERVAL_SCHEDULE_FAIL, 'add_interval_job fail')
        else:
            return Result('ok')
            
    def parse_cron_time(self,schedule):
        cron_time = {'timezone':DEFAULT_TIMEZONE}
        scheduleType = schedule.get("mode",None)
        if scheduleType == ScheduleType.WEEK:
            cron_time["day_of_week"] = schedule.get("days","")
        elif scheduleType == ScheduleType.MONTH:
            cron_time["day"] = schedule.get("days","")
            
        scheduleTime = schedule.get("exec_time","")
        keys = ["hour","minute","second"]
        arr = str(scheduleTime).split(":")
        for i in range(len(arr)):
            if arr[i] and i < len(keys):
                cron_time[keys[i]] = arr[i].strip()
                
        start_date = schedule.get("start_date",None)
        if start_date:
            fromdate = ConvertToDatetime(start_date)
            if fromdate > datetime.now():
                cron_time["start_date"] = datetime.strftime(fromdate,"%Y-%m-%d %H:%M:%S")
        else:
            cron_time["start_date"] = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
                
        return cron_time
    

    def parse_interval_time(self, schedule):
        start_date = schedule.get("start_date",None)
        if start_date:
            fromdate = ConvertToDatetime(start_date)
            if fromdate > datetime.now():
                start_date = datetime.strftime(fromdate,"%Y-%m-%d %H:%M:%S")
        else:
            start_date = datetime.strftime(datetime.now(),"%Y-%m-%d %H:%M:%S")
            
        if self.interval == 0:
            self.status = ScheduStatus.DISABLE
            
        return {'seconds':self.interval, 'start_date':start_date, 'timezone':DEFAULT_TIMEZONE}    
        
        
    
        
        
        
    