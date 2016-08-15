# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.
'''
Created on 2016年4月25日

@author: i65535
'''



import json

from ldap3 import Server, Connection, ALL, SUBTREE, AUTH_SIMPLE

from common.util import Result
from frame.Logger import WebLog, PrintStack, Log
from frame.errcode import LDAP_USER_NOT_EXIST_ERR, LDAP_USER_PWD_INVALID_ERR
from mongodb.dbconst import AUTH_LDAP
from mongoimpl.setting.ldapdbimpl import LDAPDBImpl


class LDAPServer(Server):
    
    @staticmethod
    def _is_ipv6(host):
        return False

class LDAPClient(object):
    '''
    classdocs
    '''
    @classmethod
    def new_ladp_client(cls, **args):
        ldap_server = args.get('server', '')
        ldap_port = args.get('port', '')
        base_dn = args.get('base_dn', '')
        user_name = args.get('user_name', '')
        password = args.get('password', '')
        ldap_tls = args.get('tls', '')
        
        if not (ldap_server and base_dn):
            return False
        
        self = cls(ldap_server, base_dn, ldap_port, user_name, password, ldap_tls)
        if self.verify_server():
            return self
        
        return False
    
    @classmethod
    def connet_to_default_sever(cls):
        info = LDAPDBImpl.instance().default_ldap_info()
        if info:
            return cls.new_ladp_client(**info)
        return False
    
    def __init__(self, server_ip, base_dn, port=389, user_name='admin', password='', tls=False):
        '''
        Constructor
        @param base_dn: dc=jack,dc=com
        @param username: 'cn=admin,dc=jack,dc=com' 
        @param ldap_server: ldap://192.168.12.55:389
        '''
        self.server_ip = str(server_ip)
        self.port = int(port)
        self.base_dn = base_dn
        self.user_name = 'cn=%s,%s'%(user_name, base_dn)
        self.password = password
        self.uid_key = 'uid'
        self.paged_size = 100
        
    def load_all_user(self):
        try:
            with Connection(self.server, user=self.user_name, password=self.password) as conn:
                if not conn.bind():
                    Log(2, 'load_all_user fail,as[%s]'%(conn.result.get('description','')))
        
                _filter = '(%s=*)'%(self.uid_key)
                    
                result = conn.search(search_base = self.base_dn,
                     search_filter = _filter,
                     search_scope = SUBTREE,
                     attributes = [self.uid_key, 'cn', 'givenName'],
                     paged_size = self.paged_size)
                
                result = conn.result
                Log(3,"result=%s"%(json.dumps(result)))
                if result['description'] != 'success':
                    return []
                
                Log(3,"response=%s"%(json.dumps(conn.response)))
                return conn.response
        except Exception:
            PrintStack()
            
        return False
        
    def find_user(self, user_id):
        try:
            with Connection(self.server, user=self.user_name, password=self.password) as c:
                if not c.bind():
                    Log(2, 'LDAP[%s]login fail,as[%s]'%(self.user_name, c.result.get('description','')))
        
                _filter = '(%s=%s)'%(self.uid_key, user_id)
                    
                c.search(search_base = self.base_dn,
                     search_filter = _filter,
                     search_scope = SUBTREE,
                     attributes = ['cn', 'givenName'],
                     paged_size = 5)
                
                if len(c.response) == 1:
                    return c.response[0]['dn']
        except Exception:
            PrintStack()
            
        return False
            
    def verify_pwd(self, user_dn, password):
        try:
            with Connection(self.server, user=user_dn, password=password, authentication=AUTH_SIMPLE) as c:
                if c.bind():
                    return True
        except Exception:
            PrintStack()
            
        return False
    
    def verify_user(self, user_id, password, user_dn=None):
        user_dn = user_dn if user_dn else self.find_user(user_id)
        if user_dn:
            return self.verify_pwd(user_dn, password)
        else:
            return False
        
    def verify_server(self):
        try:
            self.server = LDAPServer(self.server_ip, self.port, get_info=ALL)
            if self.server.check_availability():
                WebLog(3, 'Connect to LDAP server %s:%s success.'%(self.server_ip, self.port))
                return True
        except Exception:
            PrintStack()

        return False
    
    def read_user_info(self, user_id, password):
        user_dn = self.find_user(user_id)
        if not user_dn:
            Log(1, 'read_user_info[%s]fail.'%(user_id))
            return Result(user_id, LDAP_USER_NOT_EXIST_ERR, 'user not exist.')
        
        if self.verify_pwd(user_dn, password):
            return Result({'ldap_dn':user_dn, 'source':AUTH_LDAP, '_id':user_id})
        else:
            return Result(user_id, LDAP_USER_PWD_INVALID_ERR, 'username or password invalid.')
        
    
    