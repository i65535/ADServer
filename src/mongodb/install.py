#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
"""
initialize database ,create table and insert some system info
"""

import getopt
import sys

from frame.Logger import SysLog
from mongodb.commondb import CommonDB, Tables
from mongodb.dbconst import MAIN_DB_NAME
from mongodb.dbmgr import DBMgr


def main():
    ret = DBMgr.instance().isDBRuning()
    if not ret:
        SysLog(1,"setup fail,database error")
        return 0
    
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "ilsh", ["install","loadData","loadScript","help"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    if not len(opts):
        usage()
        sys.exit()
    for opt, _ in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-i","--install"):
            install()
            sys.exit()
        elif opt in ("-l","--loadData"):
            loadData()
            sys.exit()
        elif opt in ("-s","--loadScript"):
            loadScript()
            sys.exit()
        


def usage():
    print "-h  --help  show help"
    print "python install.py -i  [new install,it will clear user data.]"
    print "python install.py -l  [reset the prepare data,won't delete user data.]"
    print "python install.py -h  [show help]"
    
def install():
    cloud_db = CommonDB(MAIN_DB_NAME,Tables)
    cloud_db.setup()
    
    
def loadData():
    cloud_db = CommonDB(MAIN_DB_NAME,{})
    cloud_db.auto_import_data()

def loadScript():
    cloud_db = CommonDB(MAIN_DB_NAME,{})
    cloud_db.auto_load_js()

if __name__ == '__main__':
    main()

