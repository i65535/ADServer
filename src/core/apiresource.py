# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.


import json
import xmlrpclib

from twisted.internet import threads
from twisted.web import resource, server

from common.util import LawResult
from frame.Logger import SysLog


Fault = xmlrpclib.Fault

class APIResource(resource.Resource):
    NOT_FOUND = 8001
    FAILURE = 8002
    def __init__(self,service,handler,allow_none = True,useDateTime=False, encoding = "UTF-8"):
        resource.Resource.__init__(self)
        self.service = service     
        self.instance = handler
        self.isLeaf = True
        self.encoding = encoding
#        self.wwwroot = wwwroot
        
    def render_GET(self,request):
        arr = [key for key in request.postpath if key!='']

        if len(arr) == 0:
            return self.process(request, 'whatTime')
        
        return self.process(request, arr[0], arr[1:])
    
    def render_PUT(self,request):
        arr = request.path.split("/")
        if len(arr) < 4:
            return 'The url is invalid!'
        
        return self.process(request, 'Update', arr[2:] )
    
    def render_DELETE(self,request):
        arr = [key for key in request.postpath if key!='']
            
        if len(arr) == 0:
            return self.process(request, 'whatTime')
        
        act = 'delete_'+ arr[0]
        
        return self.process(request, act, arr[1:])
    
    def render_POST(self, request):
        arr = [key for key in request.postpath if key!='']
            
        if len(arr) == 0:
            return self.process(request, 'whatTime')
        elif len(arr) == 1:
            act = arr[0]
            args = []
        elif arr[1] in ['add','delete','update']:
            act = arr[1] + '_'+ arr[0]
            args = arr[2:]
        else:
            act = arr[0]
            args = arr[1:]
            
        data = request.content.read()
        if(len(data) > (2 ** 23)):
            data = 'post data too big.'
            request.content = None
        args.append(data)
        


        return self.process(request,act,args)
    
    def render_OPTIONS(self, request):
        arr = [key for key in request.postpath if key!='']
            
        if len(arr) == 0:
            return self.process(request, 'whatTime')
        
        act = 'option'+ arr[0]
        
        return self.process(request, act, arr[1:])
    
    
    def process(self,request,act,args=[]):
        headers = request.requestHeaders
        token = headers.getRawHeaders('token')

        params = {}
        for key in request.args:
            if len(request.args[key]) == 1:
                params[key] = request.args[key][0]
            else:
                params[key] = request.args[key]
        
        function = getattr(self.instance, "dispatch", None)
        if function is None:
            f = Fault(self.FAILURE, "The Resource didn't implement the _dispatch method")
            self._cbRender(f, request)
        else:
            # Use this list to track whether the response has failed or not.
            # This will be used later on to decide if the result of the
            # Deferred should be written out and Request.finish called.
            responseFailed = []
            request.notifyFinish().addErrback(responseFailed.append)
            
            d = threads.deferToThread(function,act,token,*args, **params)
            d.addErrback(self._ebRender)
            d.addCallback(self._cbRender, request, responseFailed)
        return server.NOT_DONE_YET 
        
    
    def _ebRender(self, failure):
        if isinstance(failure.value, Fault):
            return failure.value
        SysLog(1,failure)
        return Fault(self.FAILURE, "error")
    
    def _cbRender(self, result, request, responseFailed=None):
        ret = {"success":True,"message":""}
        if responseFailed:
            return
        
        result_code = 0
        
        if isinstance(result, Fault):
            ret["success"] = False
            ret["message"] = "faultCode:%d,faultString:%s"%(result.faultCode,result.faultString)
        elif isinstance(result,LawResult):
            ret = result.to_json()
            result_code = result.result
        else:
            ret = result

        try:
            content = json.dumps(ret)
            request.setHeader("content-length", str(len(content)))
            request.setHeader("Access-Control-Allow-Origin", "*")
            request.setHeader("Result-Code", result_code)
            request.write(content)
        except Exception, e:
            SysLog(1,"TestResource._cbRender fail [%s]"%str(e))
        request.finish()
