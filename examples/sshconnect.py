"""
Examples for ssh2.SSHConnect

The following examples, create a new :class:`ssh2.SSH`, executes the command
and returns a 2-tuple with the STDOUT and exit status code.
"""

from ssh2 import SSH, SSHConnect


HOSTNAME = "example.com"
USERNAME = "user"
PASSWORD = "password"
CONFIGS  = {
    "hostname": HOSTNAME,
    "username": USERNAME,
    "password": PASSWORD,
    "use_ssh_config": False
}


@SSHConnect(hostname=HOSTNAME)
def sshconnect_ex1(ssh: SSH):
    """
    SSH example using :class:`ssh2.SSHConnect` with SSH configuration 
    file (:code:`~/.ssh/config`).
    """
    return ssh.execute("ls -l")


@SSHConnect(**CONFIGS)
def sshconnect_ex2(ssh: SSH):
    """
    SSH example using :class:`ssh2.SSHConnect` with manual configuration
    arguments.
    """
    return ssh.execute("ls -l")


if __name__ == "__main__":
    sshconnect_ex1()
    sshconnect_ex2()
