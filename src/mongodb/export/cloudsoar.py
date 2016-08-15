#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.

import datetime

from mongodb.dbconst import APP_HOUSE_VERSION


def date_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


data = {}


data['User'] = [{"nick_name":"admin","password":"MTIzNDU2","_id":"admin","avatar":"","join_time":"1457958007295","role":"ring0", "source":"local"}]
data['Storage'] = [{"_id":"Local","name":"Local File System","path":""},{"_id":"GlusterFS","name":"GlusterFS","path":""}]
data['SMTP'] = [{"host":"","password":"","_id":1,"from_addr":"","port":25,"ssl":0}]
data['LDAP'] = [{"server":"", "base_dn":"", "user_name":"", "password":"","_id":1,"port":389,"tls":False}]


data['Configure'] = [{'_id':'authorize', 'value':'local'}, {'_id':'storage_type', 'value':'Local'}, {'_id':'version', 'value':APP_HOUSE_VERSION}]

