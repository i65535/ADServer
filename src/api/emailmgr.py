# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年4月26日

@author: i65535
'''
import Queue
import threading
import time

from common.util import TimestampToStr, DateNowStr
from frame.Logger import PrintStack, Log
from frame.emailsender import EmailSender, SendTask
from mongodb.dbconst import ID
from mongoimpl.setting.emaildbimpl import EmailDBImpl
from mongoimpl.setting.logdbimpl import LogDBImpl
from mongoimpl.setting.smtpdbimpl import SMTPDBImpl

ERROR_LEVEL_MASSAGE = 'ERROR'
WARNING_LEVEL_MASSAGE = 'WARNING'
INFO_LEVEL_MASSAGE = 'INFO'


class EmailMgr(object):
    '''
    # 这个类用来发送WebLog打印的日志
    '''

    def __init__(self, email_tool):
        '''
        Constructor
        '''
        super(EmailMgr, self).__init__()
        self.emailtool = email_tool
        self.task_queue = Queue.Queue()
        self.threads = []
        self.logs = []
        
        self.__init_thread_pool(1, 'SendEmailScheduler')
        self.load_email()
    
    @classmethod    
    def new_email_manager(cls):
        rlt = SMTPDBImpl.instance().default_smtp()
        if not rlt.success:
            return False
        tool = EmailSender(rlt.content)
        if not tool.test():
            return False
        
        if not hasattr(cls, "_instance"):
            cls._instance = cls(tool)
        else:
            cls._instance.emailtool = tool
        return cls._instance

        
    def __init_thread_pool(self,thread_num,schedule_name):
        while thread_num:
            name = "%s_%s"%(schedule_name,thread_num)
            thread_num -= 1
            self.threads.append(Factory(self.task_queue,name))
            
        
    def load_email(self):
        self.email1 = []
        self.email2 = []
        self.email3 = []
        rlt = EmailDBImpl.instance().read_record_list()
        if not rlt.success:
            Log(1, 'load email list fail')
            return rlt
        
        for email in rlt.content:
            if email.get('level',None) == ERROR_LEVEL_MASSAGE:
                self.email1.append(email[ID])
                
            elif email.get('level',None) == WARNING_LEVEL_MASSAGE:
                self.email2.append(email[ID])
            
            else:
                self.email3.append(email[ID])
        
    def timeout(self):
        try:
            self.process_log()
        except Exception:
            PrintStack()
            
    def load_logs(self):
        if len(self.logs):
            return True

        if self.task_queue.qsize():
            return False
        
        self.logs = LogDBImpl.instance().get_logs()
        
        return len(self.logs) > 0
            
    def process_log(self):
        if not self.load_logs():
            return
        
        error = []
        warning = []
        info = []
        ids = []
        level = ['', 'Error', 'Worning', 'Info', '']
        for log in self.logs:
            ids.append(log[ID])
            msg = '%s [%s] %s\n'%(TimestampToStr(log['time']/1000), level[log['level']], log['content'])
            info.append(msg)
            if log['level'] == 1:
                error.append(msg)
                warning.append(msg)
            elif log['level'] == 2:
                warning.append(msg)
                
        self.logs = []

        if len(error):
            self.send_error_msg(error, ids)
            
        if len(warning):
            self.send_warning_msg(warning, ids)
            
        if len(info):
            self.send_info_msg(info, ids)
        
    def send_error_msg(self, logs, ids):
        if len(self.email1) == 0:
            return LogDBImpl.instance().skip(ids)
        
        self.create_task(self.email1, 'Error message', logs, ids)
    
    def send_warning_msg(self, logs, ids):
        if len(self.email2) == 0:
            return LogDBImpl.instance().skip(ids)
        
        self.create_task(self.email2, 'Warning message', logs, ids)
    
    def send_info_msg(self, logs, ids):
        if len(self.email3) == 0:
            return LogDBImpl.instance().skip(ids)
        
        self.create_task(self.email3, 'Info message', logs, ids)
        
    def create_task(self,emails, title, logs, ids):
        logs.append('---------------------------------------------------------------\n')
        logs.append(DateNowStr())
        content = ''.join(logs)
        
        subject = '[%d]%s ---[%s]'%(len(logs)-2, title, DateNowStr())
        self.task_queue.put(SendTask(self.emailtool, emails, subject, content, ids))


class Factory(threading.Thread):
    def __init__(self, task_queue,factory_name="Factory"):
        super(Factory, self).__init__(name=factory_name)
        self.task_queue = task_queue
        self.setDaemon(True)
        self.start()
    
    def run(self):
        while True:
            try:  
                #任务异步出队，Queue内部实现了同步机制
                task = self.task_queue.get()
                task.run()
                while True:
                    if task.is_finished() :
                        #通知系统任务完成  
                        self.task_queue.task_done()
                        break
                    time.sleep(3)
                time.sleep(15)
            except Exception,e:
                PrintStack()
                Log(1,"Factory.run throw exception[%s]"%(str(e)))
            
            
        
        
        