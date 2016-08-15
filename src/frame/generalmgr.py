# -*- coding: utf-8 -*-
# Copyright (c) 20016-2016 The i65535.
# See LICENSE for details.

import os
import re
import threading

from common.guard import LockGuard, FileGuard
from frame.Logger import Log, PrintStack
from frame.configmgr import GetWorkPath, SetConfig, GetSysConfig
from mongoimpl.setting.configdbimpl import ConfigDBImpl


class GeneralMgr(object):
    '''
    '''
    __lock = threading.Lock()
    # __config_path = None
    Env = {}

    @classmethod
    def instance(cls):
        with LockGuard(cls.__lock):
            if not hasattr(cls, "_instance"):
                cls._instance = cls()
        return cls._instance

    def __init__(self):
        pass
    
    def init_general_setting(self):
        try:
            return self.get_general()
        except Exception:
            PrintStack()
            return None

    def get_general(self):
        info = {}
        info['http_port'] = self.get_host_port('install_registryui_1', 80)
        info['https_port'] = self.get_host_port('install_registryui_1', 443)
        info['domain_name'] = self.get_domain_name()
        info['ssl_crt'] = self.read_from_file("server.crt")
        info['ssl_key'] = self.read_from_file("server.key")
        Log(3, 'get_general inof [%s].'%(info))
        
        rlt = ConfigDBImpl.instance().set_general_info(info)
        if rlt.success:
            Log(3, 'update generalsetting success!')
        else:
            Log(1, 'update generalsetting fail,as[%s]'%(rlt.message))

        return info

    
    def get_domain_name(self):
        domain_match_ip = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))")
        domain = GetSysConfig('common_name')
        ip = domain_match_ip.findall(domain)
        ips = [g[0] for g in ip]
        if ips:
            return domain.split(':')[0]
        else:
            return domain
    
    def read_from_file(self, filename):
        data = ""
        file_path = self.get_ssl_file(filename)
        if not os.path.isfile(file_path):
            Log(1, "The ssl file [%s] is not exist."%(file_path))
            return data

        with open(file_path, "r") as fd:
            data = fd.read()
        return data
  
    def set_general(self, info):
        rlt = self.set_domain_name(info['domain_name'])
        if not rlt:
            Log(1, 'set domain_name file fail.')
            return rlt
        
        rlt = self.set_nginx_server_name(info['domain_name'])
        if not rlt:
            Log(1, 'set set_nginx_server_name file fail')
            return rlt

        rlt = self.set_ssl(info)
        if not rlt:
            Log(1, 'set ssl file fail')
            return rlt
        return rlt
  
    def save_to_file(self, path, data):
        if not os.path.isfile(path):
            Log(1,"The ssl file [%s] is not exist."%(path))
            return False
        with FileGuard(path,'w') as fd:
            fd.write(data)
        return True
        
    def update_conf_file(self, path, server_name):
        buf = ''
        with open(path, 'r') as cfgfile:
            for line in cfgfile:
                if line.find('server_name') >= 0:
                    if line.strip().startswith("#"):
                        buf += line
                    else:
                        buf += '\tserver_name ' + server_name + ';\n'
                else:
                    buf += line
        return self.save_to_file(path, buf)
        
    def get_nginx_conf_file(self, filename):
        path = GetWorkPath('frame', 'nginx_conf')
        if not os.path.isdir(path):
            Log(1,"The nginx conf path [%s] is not exist."%(path))
            return

        return os.path.join(path, filename)
    
    def set_nginx_server_name(self, server_name):
        registry_ui_conf = self.get_nginx_conf_file('registry_ui.conf')
        if not os.path.isfile(registry_ui_conf):
            Log(1,"The nginx conf file [%s] is not exist."%(registry_ui_conf))
            return False
            
        self.update_conf_file(registry_ui_conf, server_name)
        
        docker_registry_conf = self.get_nginx_conf_file('docker_registry.conf')
        if not os.path.isfile(docker_registry_conf):
            Log(1,"The nginx conf file [%s] is not exist."%(docker_registry_conf))
            return False
            
        self.update_conf_file(docker_registry_conf, server_name)
        
        return True

    def get_ssl_file(self, file_name):
        workdir = GetWorkPath('frame','ssl')
        return os.path.join(workdir, file_name)

    def set_domain_name(self, domain):
        if not domain:
            Log(1, 'set_domain_name fail,as the domain[%s] is invalid'%(domain))
            return False
        
        domain_match_ip = re.compile(r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))")
        ip = domain_match_ip.findall(domain)
        ips = [g[0] for g in ip]
        if ips:
            registry_host_port = self.get_host_port('install_registry_1', 5002)
            return SetConfig('common_name', '%s:%s'%(domain, registry_host_port))
        else:
            return SetConfig('common_name', domain)

    def set_ssl(self, info):
        crt_path = self.get_ssl_file("server.crt")
        if not os.path.isfile(crt_path):
            Log(1, "The ssl crt file [%s] is not exist."%(crt_path))
            return False

        rlt = self.save_to_file(crt_path, info['ssl_crt'])
        if not rlt:
            Log(1, "set ssl_crt file fail.") 
            return False

        key_path = self.get_ssl_file("server.key")
        if not os.path.isfile(key_path):
            Log(1, "The ssl key file [%s] is not exist."%(key_path))
            return False

        rlt = self.save_to_file(key_path, info['ssl_key'])
        if not rlt:
            Log(1, "set ssl_key file fail.") 
            return False

        return True
    

