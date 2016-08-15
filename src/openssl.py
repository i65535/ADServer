#!/usr/sbin/python
# -*- coding: utf-8 -*-
'''
## Copyright (C) 2012-2013 The i65535
## See LICENSE for details
'''


import os

from twisted.internet import reactor, ssl
from twisted.python import log, threadable
from twisted.python.logfile import DailyLogFile
from twisted.web import server

from core.server import WebService
from frame.Logger import PrintStack
from frame.configmgr import GetSysConfigInt


second = 0

def monitoring(): 
    global second
    second += 10
    log.msg('system running <%d> second'%second)
    reactor.callLater(10,monitoring)
    
def get_cert(workroot):
    cert_path = os.path.join(workroot,"frame")
    cert_path = os.path.join(cert_path,"ssl")
    cert_path = os.path.join(cert_path,"server.pem")
    if os.path.isfile(cert_path):
        with open(cert_path,'r') as fp:
            return fp.read()

    log.msg('cert not exist')
    return ''

def init_log(workroot):
    logdir = os.path.join(workroot,"Trace")
    logdir = os.path.join(logdir,"twisted")
    if not os.path.isdir(logdir):
        os.makedirs(logdir)
    log_file = DailyLogFile("server.log", logdir)
    log.startLogging(log_file) 

def main():   
    reactor.suggestThreadPoolSize(100)
    threadable.init(1)   # 设置线程安全
    
    workroot = os.path.dirname(os.path.abspath(__file__))
    
    init_log(workroot)
    certData = get_cert(workroot)
    if not certData:
        log.msg('system boot failure')
        return 
        
    certificate = ssl.PrivateCertificate.loadPEM(certData)
    
    webserver = WebService(workroot)
    
    port = GetSysConfigInt("server_port",8080)
    reactor.listenSSL(port, server.Site(webserver.get_resource()), certificate.options())
    reactor.callLater(10,monitoring) 
    reactor.run()
    

    
if __name__ == '__main__':
    try:
        main()
    except Exception:
        PrintStack()


