#!/usr/bin/env/python

import sys
import os
import argparse
import ConfigParser
import requests

try:
    import json
except ImportError:
    import simplejson as json

katello_ini='katello.ini'
param_list=['hostname', 'username', 'password', 'host_collections']

class KatelloHostCollection(object):
    def _empty_inventory(self):
        return { '_meta': { 'hostvars': {} } }

    def __init__(self):
        self.inventory = self._empty_inventory()
        self.read_settings()
        self.read_cli_args()

        self.katello_base_url="https://%s/katello/api" % self.hostname
        self.foreman_base_url="https://%s/api" % self.hostname

        if self.args.list:
            self.inventory = self.get_host_collection()
        else:
            self.inventory = self._empty_inventory()

        print json.dumps(self.inventory)

    def _get_host_collections_list(self):
        url="%s/organizations/1/host_collections?per_page=1000" % self.katello_base_url
        result = requests.get(url, auth=(self.username,self.password))
        if result.status_code != 200:
            raise KatelloReturnCodeError("ERROR: %s returned status code: %s" % 
                (sys._getframe().f_code.co_name, result.status_code))

        hc_list = []
        for hc in result.json()['results']:
            hc_list.append(hc)

        return hc_list

    def _get_host_collection(self,hc_id):
        url="%s/host_collections/%s" % (self.katello_base_url,str(hc_id))
        result = requests.get(url, auth=(self.username,self.password))
        if result.status_code != 200:
            raise KatelloReturnCodeError("ERROR: %s returned status code: %s" % 
                (sys._getframe().f_code.co_name, result.status_code))

        return result.json()['host_ids']

    def _get_hostname(self,host_id):
        url="%s/hosts/%s" % (self.foreman_base_url, str(host_id))
        result = requests.get(url, auth=(self.username,self.password))
        if result.status_code != 200:
            raise KatelloReturnCodeError("ERROR: %s returned status code: %s" % 
                (sys._getframe().f_code.co_name, result.status_code))

        return result.json()['facts']['network::hostname']

    def get_host_collection(self):
        data = self._empty_inventory()
        for hc_name in self.host_collections:
            host_collection = self._get_host_collections_list()
            for hc in host_collection:
                inventory = []
                if hc['name'] == hc_name:
                    hc_list = self._get_host_collection(hc['id'])
                    for host_id in hc_list:
                        hostname = self._get_hostname(host_id)
                        inventory.append(hostname)
                        data['_meta']['hostvars'][hostname] = {}
                    data[hc['name']] = inventory
        return data

    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()

    def read_settings(self):
        config = ConfigParser.SafeConfigParser()
        ini_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), katello_ini )
        config.read(ini_path)
        section = 'default'

        for param in param_list:
            if config.has_option( section, param):
                if param == 'host_collections':
                    setattr(self, param, config.get( section, param).split(','))
                else:
                    setattr(self, param, config.get(section, param))
            else:
                raise ConfigParser.NoOptionError(param,section)

class KatelloReturnCodeError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)

if __name__ == '__main__':
    KatelloHostCollection()
