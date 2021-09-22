"""
Examples for ssh2.SSHTunnelContext.

The following examples, create a new :class:`ssh2.SSH` (via tunnel), 
executes the command and returns a 2-tuple with the STDOUT and exit 
status code.
"""

from ssh2 import SSHTunnelContext, SSHConfigData


HOSTNAME = "host1.example.com"
USERNAME = "jsmith"
KEY_FILENAME = ["~/.ssh/id_rsa.host1"]
CONFIGS  = {
    "hostname": HOSTNAME,
    "username": USERNAME,
    "key_filename": KEY_FILENAME,
    "use_ssh_config": False
}

JUMP_HOSTNAME = "jump1.example.com"
JUMP_USERNAME = "jsmith"
JUMP_PASSWORD = "p@ssw0rd"
JUMP_CONFIGS  = {
    "hostname": JUMP_HOSTNAME,
    "username": JUMP_USERNAME,
    "password": JUMP_PASSWORD,
    "use_ssh_config": False
}


def sshtunnelcontext_ex1():
    """
    SSH Tunnel example using :class:`ssh2.SSHTunnelContext` with SSH 
    configuration file (:code:`~/.ssh/config`).
    """
    with SSHTunnelContext(
        SSHConfigData(hostname=JUMP_HOSTNAME),
        SSHConfigData(hostname=HOSTNAME)) as ssh:
        return ssh.execute("ls -l")


def sshtunnelcontext_ex2():
    """
    SSH Tunnel example using :class:`ssh2.SSHTunnelContext` with manual
    configuration arguments.
    """
    with SSHTunnelContext(
        SSHConfigData(**JUMP_CONFIGS),
        SSHConfigData(**CONFIGS)) as ssh:
        return ssh.execute("ls -l")


if __name__ == "__main__":
    sshtunnelcontext_ex1()
    sshtunnelcontext_ex2()