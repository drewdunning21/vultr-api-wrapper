import paramiko
import time
import requests
import os
import socket
from stat import S_ISDIR
m = __import__ ('vultr-server')
try:
    attrlist = m.__all__
except AttributeError:
    attrlist = dir (m)
for attr in attrlist:
    globals()[attr] = getattr (m, attr)

class VultrAccount:
    def __init__(self,key):
        self.key = key
        self.headers = {'API-Key': self.key}
        self.active = 0
        self.inactive = 0
        self.servers = []
        self.serverSet = set()
        self.updateServers()

    def newServer(self, dcid, vps, osid,scriptId):
        data = { 'DCID': dcid, 'VPSPLANID': vps, 'OSID': osid, 'SCRIPTID': scriptId}
        response = requests.post('https://api.vultr.com/v1/server/create', headers=self.headers, data=data)
        code = str(response.status_code)
        if '200' in code:
            subid = response.json()['SUBID']
            return Server(dcid,vps,osid,subid,self.key)
        else:
            print('There was an error: ' + code)

    def updateServers(self):
        data = self.getServersJson()
        if data != []:
            for key, value in data.items():
                cur = data[key]
                if key in self.serverSet:
                    self.updateServer(key,value)
                else:
                    self.serverSet.add(key)
                    if cur['status'] == 'active':
                        self.active += 1
                    else:
                        self.inactive += 1
                    newServer = Server(cur['DCID'],cur['VPSPLANID'],cur['OSID'],key,self.key)
                    self.servers.append(newServer)

    def updateServer(self,subid,values):
        for i in self.servers:
            if i.subid == subid:
                i.status = values['status']
                return

    def getServers(self):
        return self.servers

    def getServersJson(self):
        return requests.get('https://api.vultr.com/v1/server/list', headers=self.headers).json()

    def __str__(self):
        retStr = 'Key: ' + self.key + '\n'
        retStr += 'Server List:\n'
        for server in self.servers:
            retStr += str(server) + '\n'
        return retStr.strip('\n')
