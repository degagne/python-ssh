from __future__ import absolute_import

import copy
import paramiko
import select
import pathlib
import typing as t

from socket import error as SocketError
from paramiko.config import SSH_PORT
from paramiko.ssh_exception import (
    SSHException,
    AuthenticationException,
    BadAuthenticationType,
    BadHostKeyException
)
from ssh2.errors import SSHConnectionError, SSHConfigurationError, SSHChannelError, SFTPError


SSH_CONFIG = "~/.ssh/config"

STRING  = 1
INTEGER = 2
BOOLEAN = 3
SOCKS   = 4

CONFIG_KEY_MAPPING = (
    ("hostname", "hostname", STRING,),
    ("port", "port", INTEGER,),
    ("user", "username", STRING,),
    ("identityfile", "key_filename", STRING,),
    ("connecttimeout", "timeout", INTEGER,),
    ("forwardagent", "allow_agent", BOOLEAN,),
    ("identitiesonly", "look_for_keys", BOOLEAN,),
    ("compression", "compress", BOOLEAN,),
    ("gssapiauthentication", "gss_auth", BOOLEAN,),
    ("gssapikeyexchange", "gss_kex", BOOLEAN,),
    ("gssapidelegatecredentials", "gss_deleg_creds", BOOLEAN),
    ("proxycommand", "sock", SOCKS)
)


class SSH:
    """A high-level representation of a session with an SSH server.
    
    This class wraps the  `paramiko.SSHClient` object to simplify most aspects of
    interacting with an SSH server.

    A example use case is:

    .. code-block:: python

        ssh = SSH()
        configs = ssh.load_ssh_config("ssh.example.com")
        ssh.connect(**configs)
        output, rc = ssh.execute("ls -l")

    Instances of this class can also be used with the ``ssh_connect``
    decorator:

    .. code-block:: python

        @ssh_connect()
        def myfunction(ssh, hostname):
            configs = ssh.load_ssh_config("ssh.example.com")
            ssh.connect(**configs)
            output, rc = ssh.execute("ls -l")

        myfunction("ssh.example.com")
    """
    DEFAULT_CONFIG = {
        "hostname": None,
        "port": SSH_PORT,
        "username": None,
        "password": None,
        "key_filename": None,
        "timeout": None,
        "allow_agent": True,
        "look_for_keys": True,
        "compress": False,
        "sock": None,
        "gss_auth": False,
        "gss_kex": False,
        "gss_deleg_creds": True,
        "gss_host": None,
        "gss_trust_dns": True,
        "banner_timeout": None,
        "auth_timeout": None,
        "passphrase": None,
        "disabled_algorithms": None
    }

    def __init__(self) -> t.NoReturn:
        """
        Creates a new SSH instance.
        """
        self._client = None
        self._output = []

    def __configure(self, **configs: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
        """Verifies SSH configuration properties.

        Before SSH server connections are attempted, the SSH configuration properties
        are verified to ensure they are supported by ``paramiko.SSHClient``.

        :param dict configs: SSH configuration properties -- see ``.connect``
        :return: A dict object with supported SSH configuration properties.
        :raises: ``.SSHConfigurationError`` -- if configuration property is unsupported.
        """
        extra_configs = set(configs).difference(self.DEFAULT_CONFIG)
        if extra_configs:
            raise SSHConfigurationError(f"Unsupported configuration property (or properties): {extra_configs}")

        new_configs = copy.copy(self.DEFAULT_CONFIG)
        new_configs.update(configs)
        return new_configs

    def __connect(self, **configs: t.Dict[str, t.Any]) -> paramiko.SSHClient:
        """Establishes SSH connection to server.

        Connects to SSH server and authenticates following order of priority set by
        paramiko -- see ``paramiko.connect``.

        :param dict configs: SSH configuration properties for connection.
        :return: ``paramiko.SSHClient`` object.
        :raises: ``.SSHConnectionError`` -- if an error occurred while attempting to connect.
        """
        self.__configure(**configs)
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(**configs)
            return ssh
        except (SocketError,
                SSHException,
                AuthenticationException,
                BadAuthenticationType,
                BadHostKeyException) as err:
            raise SSHConnectionError(f"Connection to '{configs['hostname']}' failed with error: {err}")

    @classmethod
    def load_ssh_config(cls, hostname: str, config_file: t.Optional[str] = SSH_CONFIG) -> t.Dict[str, t.Any]:
        """Loads SSH configuration properties.

        Generates a dict with supported keyword/values from the ssh_config directives.

        :param str hostname: The remote server to connect to.
        :param str config_file: The filename for the ssh_config. Default: ``~/.ssh/config``
        :return: A dict object with supported SSH configuration properties.
        :raises: ``.SSHConfigurationError`` -- if SSH configuration file cannot be found.
        """
        config_file = pathlib.Path(config_file).expanduser()
        if not config_file.exists():
            raise SSHConfigurationError(f"SSH configuration file '{config_file}' cannot be found.")

        configs_dict = paramiko.config.SSHConfigDict()
        ssh_config = paramiko.SSHConfig().from_path(config_file).lookup(hostname)

        for (key, value, value_type) in CONFIG_KEY_MAPPING:
            if key in ssh_config:
                configs_dict.update({value: ssh_config[key]})
                if value_type == INTEGER:
                    configs_dict.update({value: configs_dict.as_int(value)})
                if value_type == BOOLEAN:
                    configs_dict.update({value: configs_dict.as_bool(value)})
                if value_type == SOCKS:
                    configs_dict.update({value: paramiko.ProxyCommand(ssh_config[key])})

        return configs_dict

    def disconnect(self) -> t.NoReturn:
        """Close SSH connection.

        Terminates SSH connection and its underlying ``paramiko.Transport``.
        """
        if isinstance(self._client, paramiko.SSHClient):
            self._client.close()

    def connect(self, **configs: t.Dict[str, t.Any]) -> t.NoReturn:
        """Connect to an SSH server and authenticate to it.

        The preferred method for passing the supported keyword arguments is through 
        the ``.load_ssh_config`` function. This function uses the ``~/.ssh/config`` 
        file to build the configs dict.

        .. code-block:: python

            configs = ssh.load_ssh_config("example.com")
            ssh.connect(**configs)

        :param str hostname: The remote server to connect to.
        :param int port: The remote server port to connect to. Default: 22.
        :param str username: The username to authenticate as. Default: current local username.
        :param str password: The password to authenticate with.
        :param key_filename: 'filename' string (or list of 'filename' strings) of optional
            private key(s) and/or certs to try for authentication.
        :param float timeout: An optional timeout (in seconds) for the TCP connection.
        :param bool allow_agent: Enables/disables connecting to the SSH agent. 
            Default: True.
        :param bool look_for_keys: Enables/disables searching for discoverable private key
            files in ``~/.ssh/``. Default: True.
        :param bool compress: Enables/disables compressions. Default: False.
        :param socket sock: A socket or socket-like object to use for communication to the 
            target host.
        :param bool gss_auth: Enables/disables GSS-API authentication. Default: False.
        :param bool gss_kex: Enables/disables GSS-API key exchange and user authentication.
            Default: False.
        :param bool gss_deleg_creds: Enables/disables delegatation of GSS-API client 
            credentials. Default: True.
        :param bool gss_host: The targets name in the Kerberos database. Default: None.
        :param bool gss_trust_dns: Indicates whether or not the DNS is trusted to 
            securely canonicalize the name of the host being connected to. Default: True.
        :param float banner_timeout: An optional timeout (in seconds) to wait for the 
            SSH banner to be presented.
        :param float auth_timeout: An optional timeout (in seconds) to wait for an 
            authentication response.
        :param str passphrase: Used for decrypting private keys.
        :param dict disabled_algorithms: An optional dictionary passed directly to 
            ``.Transport`` and its keyword argument of the same name. 
        """
        self._client = self.__connect(**configs)

    def open_tunnel(self, dest_hostname: str, dest_port: t.Optional[int] = SSH_PORT, **configs: t.Dict[str, t.Any]) -> paramiko.Channel:
        """Requests a new channel through an intermediary host.

        Creates a socket-like object used for establish connects to unreachable hosts,
        similarily to how the ``paramiko.ProxyCommand`` works.

        :param str dest_hostname: The destination hostname of this port forwarding.
        :param int dest_port: The destination port. Default 22.
        :param dict configs: SSH configuration properties for connection.
        :return: ``paramiko.Channel`` object
        :raises: ``.SSHChannelError`` -- if transport channel encounters an error

        Example usage:

        .. code-block:: python

            # Create socket connection to remote 'jump' host
            tunnel_configs = ssh.load_ssh_config("ssh.example1.com")
            sock = ssh.open_tunnel("ssh.example2.com", **tunnel_configs)

            # Load SSH configuration and update 'sock' with our socket connection.
            configs = ssh.load_ssh_config("ssh.example2.com")
            configs.update(sock=sock)

            # Connect to SSH host and execute command.
            ssh.connect(**configs)
            ssh.execute_realtime("hostname -f")
        """
        dest_addr = (dest_hostname, dest_port)
        tunnel_addr = (configs.get("hostname"), configs.get("port", SSH_PORT))
        tunnel = self.__connect(**configs)
        tunnel_transport = tunnel.get_transport()
        try:
            return tunnel_transport.open_channel("direct-tcpip", dest_addr, tunnel_addr)
        except SSHException as err:
            raise SSHChannelError(f"Transport channel for '{dest_hostname}' failed with: {err}")

    def open_sftp(self):
        """Open an SFTP session on the SSH server.

        Note:
            This exposes the ``paramiko.open_sftp`` session object, please view the
            documentation at http://docs.paramiko.org/en/stable/api/sftp.html.

        :return: ``.SFTPClient`` session object
        """
        if not isinstance(self._client, paramiko.SSHClient):
            raise SFTPError(f"Unable to establish SFTP session on non-existent `SSHClient` object.")
        return self._client.open_sftp()

    def __execute(self, command: str, file: t.Union[t.TextIO, str] = None) -> t.Tuple[str, int]:
        """Execute a command on the SSH server.

        The command's output stream is returned along with the status code, with the 
        option to save the output to a local file.

        :param str command: The command to execute.
        :param file: An optional file-pointer object to write output to.
        :return: output and status code of the executing command, as a 2-tuple.
        """
        stdin, stdout, stderr = self._client.exec_command(command)
        channel = stdout.channel
        stdin.close() # close stdin pseudo file -- not needed
        channel.shutdown_write() # shutdown writes on the stdout channel

        self._output.append(channel.recv(len(channel.in_buffer)).decode("utf-8"))
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            readq, _, _ = select.select([channel], [], [], 0.0)
            for c in readq:
                if c.recv_ready():
                    self._output.append(channel.recv(len(c.in_buffer)).decode("utf-8"))
                if c.recv_stderr_ready():
                    self._output.append(stderr.channel.recv_stderr(len(c.in_stderr_buffer)).decode("utf-8"))
            if channel.exit_status_ready() and not channel.recv_stderr_ready() and not channel.recv_ready():
                channel.shutdown_read() # shutdown reads on the stdout channel
                channel.close() # close stdout the channel
                break

        stdout.close() # close stdout pseudo file
        stderr.close() # close stderr pseudo file

        if file:
            file.write("".join(self._output))
        return "".join(self._output), channel.recv_exit_status()

    def execute_realtime(self, command: str) -> int:
        """Execute a command on the SSH server.

        The command's output stream is immediately printed to the terminal.

        :param str command: The command to execute.
        :return: status code of the executing command

        Example usage:

        .. code-block:: python

            ssh = SSH()
            configs = ssh.load_ssh_configs("ssh.example.com")
            ssh.connect(**configs)
            rc = ssh.execute_realtime("ls -l")
        """
        stdin, stdout, stderr = self._client.exec_command(command, get_pty=True)
        channel = stdout.channel
        stdin.close() # close stdin pseudo file -- not needed
        channel.shutdown_write() # shutdown writes on the stdout channel

        for line in iter(stdout.readline, ""): print(line, end="")

        channel.shutdown_read() # shutdown reads on the stdout channel
        channel.close() # close stdout the channel
        return channel.recv_exit_status()

    def execute(self, command: str) -> t.Tuple[str, int]:
        """Execute a command on the SSH server.

        The command's output stream is returned along with the status code.

        :param str command: The command to execute.
        :return: output and status code of the executing command, as a 2-tuple.

        Example usage:

        .. code-block:: python

            ssh = SSH()
            configs = ssh.load_ssh_configs("ssh.example.com")
            ssh.connect(**configs)
            out, rc = ssh.execute("ls -l")
        """
        return self.__execute(command)

    def execute_file(self, command: str, file: t.TextIO) -> t.Tuple[str, int]:
        """Execute a command on the SSH server.

        The command's output stream is returned along with the status code as 
        well as the output stream is written to a local file.

        :param str command: The command to execute.
        :param file: A file-pointer object to write output to.
        :return: output and status code of the executing command, as a 2-tuple.

        Example usage:

        .. code-block:: python

            ssh = SSH()
            configs = ssh.load_ssh_configs("ssh.example.com")
            ssh.connect(**configs)

            with open("example.txt", "w") as file:
                ssh.execute_file("ls -l", file)
        """
        return self.__execute(command, file)