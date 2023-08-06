import fabric
import paramiko
from . import commands
import os
from stat import S_ISDIR, S_ISREG
import threading
from rs4 import pathtool

CONNINFO = {}
def get_cli ():
    global CONNINFO
    cli = connect (**CONNINFO).sftp_client ()
    cli.open ()
    return cli

THREADS = 4
LOCK = threading.Lock ()
CLIS = []

def upload (path, target, overwrite = False, id = None):
    global CLIS
    with LOCK:
        if not CLIS:
            CLIS = [get_cli () for i in range (THREADS)]
        cli = CLIS.pop (0)

    try:
        try:
            if overwrite or not cli.isfile (target):
                with LOCK:
                    cli.mkdir (os.path.dirname (target), True)
                cli.put (path, target)
        except Exception as e:
            e.id = id
            raise e

    finally:
        with LOCK:
            CLIS.append (cli)
    return id

def download (path, target, overwrite = False, id = None):
    global CLIS
    with LOCK:
        if not CLIS:
            CLIS = [get_cli () for i in range (THREADS)]
        cli = CLIS.pop (0)

    try:
        try:
            if overwrite or not os.path.isfile (target):
                with LOCK:
                    pathtool.mkdir (os.path.dirname (target))
                cli.get (path, target)
        except Exception as e:
            try:
                os.remove (target)
            except:
                pass
            e.id = id
            raise e

    finally:
        with LOCK:
            CLIS.append (cli)
    return id


def configure (host, user, password = None, key_file = None, port = 22, threads = 4):
    global CONNINFO, THREADS
    THREADS = threads
    CONNINFO = dict (
        host = host, user = user, password = password, key_file = key_file, port = port
    )

class SFTP:
    def __init__ (self, host, user, password = None, key_file = None, port = 22):
        self._host = host
        self._user = user
        self._port = port
        self._key_file = key_file
        self._password = password
        self._ssh, self._sftp = None, None

    def __getattr__ (self, attr):
        return getattr (self._sftp, attr)

    def __enter__ (self):
        self.open ()
        return self

    def __exit__ (self, *args):
        self.close ()

    def close (self):
        self._sftp.close()
        self._ssh.close()
        self._ssh, self._sftp = None, None

    def open (self):
        self._ssh = paramiko.SSHClient ()
        self._ssh.set_missing_host_key_policy (paramiko.AutoAddPolicy())
        self._ssh.connect (self._host, username = self._user, password = self._password, key_filename = self._key_file, port = self._port)
        self._sftp = self._ssh.open_sftp ()

    def mkdir (self, remote, recursive = False):
        if not recursive:
            return self._sftp.mkdir (remote)

        if self.isdir (remote):
            return

        dirs_ = []
        dir_ = remote
        while len(dir_) > 1:
            dirs_.append(dir_)
            dir_, _  = os.path.split(dir_)

        if len(dir_) == 1 and not dir_.startswith("/"):
            dirs_.append(dir_)

        while len(dirs_):
            dir_ = dirs_.pop()
            if not self.isdir (dir_):
                self._sftp.mkdir(dir_)

    def isdir (self, path):
        try:
            return S_ISDIR (self._sftp.stat (path).st_mode)
        except IOError:
            return False

    def isfile (self, path):
        try:
            return S_ISREG (self._sftp.stat (path).st_mode)
        except IOError:
            return False

    def rmdir (self, path, recursive = False):
        if not recursive:
            self._sftp.rmdir (path)
        else:
            files = self._sftp.listdir (path)
            for f in files:
                filepath = os.path.join (path, f)
                try:
                    self._sftp.remove (filepath)
                except IOError:
                    self.rmdir (filepath, True)
            self._sftp.rmdir (path)


class Connection (fabric.Connection):
    def __init__ (self, host, user, port = 22, connect_kwargs = None, postprocessing = True):
        super ().__init__ (host, user, port = port, connect_kwargs = connect_kwargs)
        self.postprocessing = postprocessing
        self.identify_system ()

    def sftp_client (self):
        return SFTP (self.host, self.user, self.connect_kwargs.get ('password'), self.connect_kwargs.get ('key_file'), self.port)

    def identify_system (self):
        r = self.run ('uname -a')
        if r.stdout.find ('Ubuntu') != -1:
            self.os = 'ubuntu'
        else:
            self.os = 'centos'

    def install (self, *apps):
        try:
            r = self.sudo ('apt install -y {}'.format (" ".join (apps)))
        except Exception as e:
            if e.result.return_code != 1:
                print ('  - error: ' + e.result.stderr)
            return False
        return True

    def run (self, cmd, *args, **kargs):
        x = super ().run (cmd, hide = True, *args, **kargs)
        if cmd.startswith ("sudo"):
            cmd = cmd [5:]
        pcmd = cmd.split ()[0]
        rclass = commands.default
        if self.postprocessing and hasattr (commands, pcmd.replace ('-', '_')):
            rclass = getattr (commands, pcmd.replace ('-', '_'))

        r = rclass.Result (x.stdout, cmd)
        x.command = cmd
        x.header = r.header
        x.meta = r.meta
        x.data = r.data
        return x

    def sudo (self, cmd):
        if 'password' in self.connect_kwargs:
            r = self.run ('echo "{}" | sudo -S {}'.format (self.connect_kwargs ['password'], cmd))
        else:
            r = self.run ('sudo {}'.format (cmd))
        return r


def connect (host, user = 'ubuntu', password = None, key_file = None, port = 22, postprocessing = True):
    if hasattr (host, 'public_dns_name'):
        host = host.public_dns_name
    if key_file:
        connect_kwargs = dict (key_filename = key_file)
    else:
        connect_kwargs = dict (password = password)
    return Connection (host, user, port, connect_kwargs = connect_kwargs, postprocessing = postprocessing)
