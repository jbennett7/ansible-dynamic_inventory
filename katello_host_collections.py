import requests
import argparse
import os
import sys
import json

hostname='host.example.com'
username='admin'
password='password'

katello_base_url="https://%s/katello/api" % hostname
foreman_base_url="https://%s/api" % hostname


class KatelloHostCollection(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        if self.args.list:
            self.inventory = self.get_host_collection(host_collection)
        else:
            self.inventory = {}

        print json.dumps(self.inventory)

    def _get_host_collections_list(self):
        url="%s/organizations/1/host_collections" % katello_base_url
        result = requests.get(url, auth=(username,password))
        if result.status_code != 200:
            raise ValueError("ERROR: %s returned status code: %s" % (sys._getframe().f_code.co_name, result.status_code))

        hc_list = []
        for hc in result.json()['results']:
            hc_list.append(hc)

        return hc_list

    def _get_host_collection(self,hc_id):
        url="%s/host_collections/%s" % (katello_base_url,str(hc_id))
        result = requests.get(url, auth=(username,password))
        if result.status_code != 200:
            raise ValueError("ERROR: %s returned status code: %s" % (sys._getframe().f_code.co_name, result.status_code)

        return result.json()['host_ids']

    def get_hostname(self,host_id):
        url="%s/hosts/%s" % (foreman_base_url, str(host_id))
        result = requests.get(url, auth=(username,password))
        if result.status_code != 200:
            raise ValueError("ERROR: %s returned status code: %s" % (sys._getframe().f_code.co_name, result.status_code))

        return result.json()['facts']['network::hostname']

    def get_host_collection(self,host_collection):

        host_collections = self._get_host_collections_list()

        inventory = []
        for hc in host_collections:
            if hc['name'] == host_colleciton:
                for host_id in self._get_host_collection(hc['id']):
                    inventory.append(self._get_hostname(host_id))

        return { host_collection: inventory }

    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        self.args = parse_args()

if __name__ == '__main__':
    KatelloHostCollection()
