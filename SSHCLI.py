from io import StringIO
import paramiko


class SshClient:
    "A wrapper of paramiko.SSHClient"
    TIMEOUT = 4

    def __init__(self, host, port, username, password, pkey_path):
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key = paramiko.RSAKey.from_private_key_file(pkey_path)
        # if key is not None:
        self.client.connect(
            host,
            port,
            username=username,
            password=password,
            pkey=key,
            timeout=self.TIMEOUT,
        )

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(self, command, sudo=True):
        feed_password = False
        if sudo and self.username != "root":
            command = "sudo -S -p '' %s" % command
            feed_password = (
                self.password is not None and len(self.password) > 0
            )
        stdin, stdout, stderr = self.client.exec_command(command)
        if feed_password:
            stdin.write(self.password + "\n")
            stdin.flush()
        return {
            "out": stdout.readlines(),
            "err": stderr.readlines(),
            "retval": stdout.channel.recv_exit_status(),
        }


if __name__ == "__main__":
    client = SshClient(
        host="host", port=22, username="username", password="password"
    )
    try:
        ret = client.execute("dmesg", sudo=True)
        print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
    finally:
        client.close()
