# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.


CLOUD_NODE_ERROR = 10000
ADAPTER_ERROR          = CLOUD_NODE_ERROR + 1000

class OPException(Exception):
    def __init__(self,value,errid=1):
        self.value = value
        self.errid = errid
    def __str__(self):
        return repr(self.value)

class InternalException(Exception):
    '''
    # 内部异常代表该异常是运行环境等原因导致的异常，
    # 内部异常通常无法通过代码处理，记日志即可。
    '''

    def __init__(self,value,errid=99):
        '''
        Constructor
        '''
        self.value = value
        self.errid = errid
    
    
    def __str__(self):
        return str({"error_code":self.errid,"message":self.value})
    