Usage
#####

The following provides usage examples.

.. note::

    The following examples assumes you are using an SSH configuraton file (i.e. ``~/.ssh/config``). You can view the 
    supported keywords accepted at :ref:`ssh_connect` for instances where a SSH configuration file isn't used.

execute
=======

Executes command on remote host and returns a 2-tuple (output and status code) object.

.. code-block:: python
    :caption: Python
    :linenos:

    from ssh import SSH, ssh_connect

    @ssh_connect()
    def example(ssh: SSH, hostname: str):
        configs = ssh.load_ssh_config(hostname)
        ssh.connect(**configs)
        output, rc = ssh.execute("ls -l")
        print(output)

execute_realtime
================

Executes command on remote host, prints output to terminal in real-time and returns the status code when execution is finished.

.. code-block:: python
    :caption: Python
    :linenos:

    from ssh import SSH, ssh_connect

    @ssh_connect()
    def example(ssh: SSH, hostname: str):
        configs = ssh.load_ssh_config(hostname)
        ssh.connect(**configs)
        rc = ssh.execute_realtime("ls -l")

execute_file
============

Executes command on remote host, writes output to local file and returns 2-tuple (output and status code) object.

.. code-block:: python
    :caption: Python
    :linenos:

    from ssh import SSH, ssh_connect

    @ssh_connect()
    def example(ssh: SSH, hostname: str):
        configs = ssh.load_ssh_config(hostname)
        ssh.connect(**configs)
        with open("example.txt", "w") as file:
            ssh.execute_file("ls -l", file)

open_tunnel
===========

Creates socket-like tunnel connection, executes command on remote host and returns 2-tuple (output and status code) object.

.. code-block:: python
    :caption: Python
    :linenos:

    from ssh import SSH, ssh_connect

    @ssh_connect()
    def example(ssh: SSH, hostname: str):
        # Create socket connection to remote 'jump' host
        tunnel_configs = ssh.load_ssh_config("ssh.example1.com")
        sock = ssh.open_tunnel("ssh.example2.com", **tunnel_configs)

        # Load SSH configuration and update 'sock' with our socket connection.
        configs = ssh.load_ssh_config("ssh.example2.com")
        configs.update(sock=sock)

        # Connect to SSH host and execute command.
        ssh.connect(**configs)
        out, rc = ssh.execute("hostname -f")
        print(out)

open_sftp
=========

Opens SFTP session.

.. note::

    This exposes the ``paramiko.open_sftp`` session object, please view the documentation at http://docs.paramiko.org/en/stable/api/sftp.html

.. code-block:: python
    :caption: Python
    :linenos:

    from ssh import SSH, ssh_connect

    @ssh_connect()
    def example(ssh: SSH, hostname: str):
        configs = ssh.load_ssh_config(hostname)
        ssh.connect(**configs)
        sftp = ssh.open_sftp()
        out = sftp.listdir()
        print(out)
