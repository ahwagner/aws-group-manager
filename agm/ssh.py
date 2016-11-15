import paramiko
import time


class Client:

    def __init__(self, host, key, username):
        self.host = host
        self.key = paramiko.RSAKey.from_private_key_file(key)
        self.user = username
        self._client = paramiko.client.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._connect()

    def _connect(self):
        self._client.connect(self.host, pkey=self.key, username=self.user)

    def send_command(self, command):
        sleep_time = 0.01
        out, err = '', ''
        transport = self._client.get_transport()
        chan = transport.open_session()
        chan.setblocking(0)
        chan.exec_command(command)
        while True:  # monitoring process
            # Reading from output streams
            while chan.recv_ready():
                out += chan.recv(1000).decode('utf-8')
            while chan.recv_stderr_ready():
                err += chan.recv_stderr(1000).decode('utf-8')
            if chan.exit_status_ready():  # If completed
                break
            time.sleep(sleep_time)
        out = [x.strip() for x in out.splitlines()]
        err = [x.strip() for x in err.splitlines()]
        return Bunch(stdout=out, stderr=err)

    def send_commands(self, command_list):
        if isinstance(command_list, str):
            return self.send_command(command_list)
        cmd = "\n".join(command_list)
        return self.send_command(cmd)


class Bunch:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)