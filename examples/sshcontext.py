"""
Examples for ssh2.SSHContext

The following examples, create a new :class:`ssh2.SSH`, executes the command
and returns a 2-tuple with the STDOUT and exit status code.
"""

from ssh2 import SSH, SSHContext


HOSTNAME = "example.com"
USERNAME = "user"
KEY_FILENAME = ["~/.ssh.id_rsa.user"]
CONFIGS  = {
    "hostname": HOSTNAME,
    "username": USERNAME,
    "key_filename": KEY_FILENAME,
    "use_ssh_config": False
}


def sshcontext_ex1():
    """
    SSHContext example using SSH configuration file (~/.ssh/config).
    """
    with SSHContext(hostname=HOSTNAME) as ssh:
        return ssh.execute("ls -l")


def sshcontext_ex2():
    """
    SSHContext example using manual configurations.
    """
    with SSHContext(**CONFIGS) as ssh:
        return ssh.execute("ls -l")


if __name__ == "__main__":
    sshcontext_ex1()
    sshcontext_ex2()
