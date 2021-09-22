"""
Examples for ssh2.SSH

The following examples, create a new :class:`ssh2.SSH`, executes the command
and returns a 2-tuple with the STDOUT and exit status code.
"""

from ssh2 import SSH, SSHConfigData, SSHConnectionError


HOSTNAME = "example.com"
USERNAME = "user"
PASSWORD = "password"


def ssh_ex1():
    """
    SSH example using :class:`ssh2.SSH` with SSH configuration 
    file (:code:`~/.ssh/config`).
    """
    try:
        ssh = SSH()
        configs = SSHConfigData(hostname=HOSTNAME)
        ssh.connect(configs)
        return ssh.execute("ls -l")
    except SSHConnectionError as err:
        print(f"SSH error: {err}")


def ssh_ex2():
    """
    SSH example using :class:`ssh2.SSH` with manual SSH configuration
    arguments.
    """
    try:
        ssh = SSH()
        configs = SSHConfigData(
            hostname=HOSTNAME,
            username=USERNAME,
            password=PASSWORD, 
            use_ssh_config=False
        )
        ssh.connect(configs)
        return ssh.execute("ls -l")
    except SSHConnectionError as err:
        print(f"SSH error: {err}")


if __name__ == "__main__":
    ssh_ex1()
    ssh_ex2()
