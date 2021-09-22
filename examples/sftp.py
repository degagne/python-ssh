"""
Examples for ssh2.SSH (SFTP)

The following examples, create a new :class:`ssh2.SSH`, opens an SFTP session
and returns the output.
"""

from ssh2 import SSH, SSHConfigData, SSHConnect, SSHContext


HOSTNAME = "example.com"


def sftp_ex1():
    """
    SSH example using :class:`ssh2.SSH` with SSH configuration 
    file (:code:`~/.ssh/config`).
    """
    ssh = SSH()
    configs = SSHConfigData(hostname=HOSTNAME)
    ssh.connect(configs)
    sftp = ssh.open_sftp()
    return sftp.listdir()


@SSHConnect(hostname=HOSTNAME)
def sftp_ex2(ssh: SSH):
    """
    SFTP example using :class:`ssh2.SSHConnect` with SSH configuration 
    file (:code:`~/.ssh/config`).
    """
    sftp = ssh.open_sftp()
    return sftp.listdir()


def sftp_ex3():
    """
    SFTP example using :class:`ssh2.SSHContext` with SSH configuration 
    file (:code:`~/.ssh/config`).
    """
    with SSHContext(hostname=HOSTNAME) as ssh:
        sftp = ssh.open_sftp()
        return sftp.listdir()


if __name__ == "__main__":
    sftp_ex1()
    sftp_ex2()
    sftp_ex3()
