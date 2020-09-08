import requests
from stat import S_ISDIR
m = __import__ ('vultr-account')
try:
    attrlist = m.__all__
except AttributeError:
    attrlist = dir (m)
for attr in attrlist:
    globals()[attr] = getattr (m, attr)
import paramiko

class Server:
    def __init__(self, dcid, vps, osid, subid,key):
        self.subid = subid
        self.key = key
        self.info = self.getInfo()
        self.dcid = self.info['DCID']
        self.vps = self.info['VPSPLANID']
        self.osid = self.info['OSID']
        self.ip = self.info['main_ip']
        self.pw = self.info['default_password']
        self.status = self.info['status']
        self.connected = False
        self.ssh = None
        self.stdin = []
        self.stdout = []
        self.stderr = []
        self.task = 'None'
        self.isSetup = False
        # self.connect()
        # self.setup()

    def getInfo(self):
        headers = {'API-Key': self.key}
        response = requests.get('https://api.vultr.com/v1/server/list', headers=headers)
        return response.json()[self.subid]

    def getSubid(self):
        return self.subid

    def connect(self):
        if self.connected:
            return
        self.info = self.getInfo()
        self.ip = self.info['main_ip']
        self.status = self.info['status']
        while True:
            try:
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh.connect(self.ip, 22, 'root', self.pw,timeout=10)
                self.connected = True
                break
            except Exception as e:
                time.sleep(2)
        return True

    def sendRemote(self,command):
        # remote = self.ssh.invoke_shell()
        remote = self.ssh.get_transport().open_session()
        buff = ''
        remote.exec_command(command)
        while 'DONE NOW' not in buff:
            resp = remote.recv(9999).decode("utf-8").strip('\n')
            if resp != '':
                buff += resp
                print(resp)
        remote.close()


    def getStdOut(self):
        return self.stdout

    def getOutput(self):
        return self.remote.recv(5000)

    def sendCommand(self,command):
        if not self.connected:
            return
        self.stdin, self.stdout, self.stderr = self.ssh.exec_command(command)
        self.stdout = ''.join(self.stdout.readlines())
        self.stderr = ''.join(self.stderr.readlines())
        return self.stdout

    def copyFile(self, origin, destination):
        if destination[-1] == '/':
            line = self.sendCommand('if test -d ' + destination + '; then echo "1"; fi')
            if '1' not in line:
                self.sendCommand('mkdir ' + destination)
        sftp = self.ssh.open_sftp()
        sftp.put(origin,destination)
        sftp.close()
        return

    def waitForNode(self):
        start = time.time()
        while self.sendCommand('node -v') == '':
            time.sleep(2)

    def waitForChromium(self):
        start = time.time()
        while 'installed' not in self.sendCommand('snap info chromium'):
            time.sleep(5)

    def disconnect(self):
        self.ssh.close()
        self.connected = False
        self.ssh = None

    def dirExists(self,path):
        return self.sendCommand('if test -d ' + path + '; then echo "1"; fi') == '1'

    def destroy(self):
        headers = { 'API-Key': self.key }
        data = { 'SUBID': self.subid }
        response = requests.post('https://api.vultr.com/v1/server/destroy', headers=headers, data=data)

    def __str__(self):
        # info = self.getInfo
        retStr = 'SubId ' + self.subid + '\n'
        retStr += 'Status: ' + self.status + '\n'
        retStr += 'Task: ' + self.task + '\n'
        return retStr

