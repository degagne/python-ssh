import paramiko
import select
import typing as t

from socket import error as SocketError
from paramiko.config import SSH_PORT
from paramiko.ssh_exception import (
    SSHException,
    AuthenticationException,
    BadAuthenticationType,
    BadHostKeyException
)
from ssh2.config import SSHConfigData
from ssh2.errors import SSHConnectionError
from ssh2.errors import SSHConfigurationError
from ssh2.errors import SSHChannelError
from ssh2.errors import SFTPError


class SSH:
    """
    A high-level representation of a session with an SSH server.
    
    This class wraps the  :class:`paramiko.SSHClient` object to simplify most 
    aspects of interacting with an SSH server.
    """

    def __init__(self) -> t.NoReturn:
        self._client = None
        self._output = []

    @classmethod
    def _connect(cls, configs: SSHConfigData) -> paramiko.SSHClient:
        """
        Returns the :class:`paramiko.SSHClient` object.

        Connects to SSH server and authenticates following order of priority 
        set by paramiko -- see :class:`paramiko.connect`.

        :param configs: :class:`ssh2.config.SSHConfigData` object.
        :return: :class:`paramiko.SSHClient` object.
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys(configs.host_key_file)
            ssh.set_missing_host_key_policy(configs.host_key_policy)
            ssh.connect(**dict(configs))
            return ssh
        except (SocketError,
                SSHException,
                AuthenticationException,
                BadAuthenticationType,
                BadHostKeyException,
                IOError,
                SSHConfigurationError) as err:
            raise SSHConnectionError(
                f"Connection to '{configs.hostname}' failed with "
                f"error: {err}")

    def connect(self, configs: SSHConfigData) -> None:
        """
        Establishes SSH connection to server.

        Connects to SSH server and authenticates following order of priority 
        set by paramiko -- see :class:`paramiko.connect`.

        :param configs: :class:`ssh2.config.SSHConfigData` object.
        :return: None.
        """
        self._client = SSH._connect(configs)

    def disconnect(self) -> t.NoReturn:
        """
        Close SSH connection.

        Terminates SSH connection and its underlying 
        :class:`paramiko.Transport`.
        """
        if isinstance(self._client, paramiko.SSHClient):
            self._client.close()

    def open_tunnel(
        self,
        configs: SSHConfigData,
        dest_hostname: str,
        dest_port: t.Optional[int] = SSH_PORT,
    ) -> paramiko.Channel:
        """
        Requests a new channel through an intermediary host.

        Creates a socket-like object used for establish connects to 
        unreachable hosts, similarily to how the 
        :class:`paramiko.ProxyCommand` works.

        :param dest_hostname: The destination hostname of this port 
            forwarding.
        :param dest_port: The destination port. Default 22.
        :param configs: :class:`ssh2.config.SSHConfigData` object.
        :return: :class:`paramiko.Channel` object.
        :raises: :class:`ssh2.errors.SSHChannelError` 
        """
        tunnel = SSH._connect(configs)
        tunnel_transport = tunnel.get_transport()
        try:
            return tunnel_transport.open_channel(
                "direct-tcpip",
                (dest_hostname, dest_port),
                (configs.hostname, configs.port)
            )
        except SSHException as err:
            raise SSHChannelError(
                f"Transport channel for '{dest_hostname}' failed with: {err}")


    def open_sftp(self):
        """
        Open an SFTP session on the SSH server.

        Note:
            This exposes the :class:`paramiko.open_sftp` session object, please 
            view the documentation at 
            http://docs.paramiko.org/en/stable/api/sftp.html.

        :return: :class:`paramiko.SFTPClient` session object
        """
        if not isinstance(self._client, paramiko.SSHClient):
            raise SFTPError(
                f"Unable to establish SFTP session on non-existent "
                "`SSHClient` object.")
        return self._client.open_sftp()

    def execute_realtime(self, command: str) -> int:
        """
        Execute a command on the SSH server.

        The command's output stream is immediately printed to the terminal.

        :param command: command to execute.
        :return: exit status code of the executing command
        """
        stdin, stdout, stderr = self._client.exec_command(
            command, get_pty=True)
        channel = stdout.channel
        stdin.close() # close stdin pseudo file -- not needed
        stderr.close() # close stderr pseudo file -- not needed
        channel.shutdown_write() # shutdown writes on the stdout channel

        for line in iter(stdout.readline, ""): print(line, end="")

        channel.shutdown_read() # shutdown reads on the stdout channel
        channel.close() # close stdout the channel
        return channel.recv_exit_status()

    def execute(
        self, 
        command: str, 
        file: t.Optional[t.Union[None, t.TextIO]] = None
    ) -> t.Tuple[str, int]:
        """
        Execute a command on the SSH server.

        The command's output stream is returned along with the exit 
        status code.

        :param command: command to execute.
        :param file: an optional file-pointer object to write the 
            output to.
        :return: a 2-tuple with the STDOUT and exit status code of the 
            executing command.
        """
        stdin, stdout, stderr = self._client.exec_command(command)
        channel = stdout.channel
        stdin.close() # close stdin pseudo file -- not needed
        channel.shutdown_write() # shutdown writes on the stdout channel

        self._output.append(
            channel.recv(len(channel.in_buffer)).decode("utf-8"))
        
        while not channel.closed or channel.recv_ready() \
            or channel.recv_stderr_ready():
            readq, _, _ = select.select([channel], [], [], 0.0)
            for c in readq:
                if c.recv_ready():
                    self._output.append(
                        channel.recv(len(c.in_buffer)).decode("utf-8"))
                if c.recv_stderr_ready():
                    self._output.append(
                        stderr.channel.recv_stderr(
                            len(c.in_stderr_buffer)).decode("utf-8"))
            if channel.exit_status_ready() \
                and not channel.recv_stderr_ready() \
                and not channel.recv_ready():
                channel.shutdown_read() # shutdown reads on the stdout channel
                channel.close() # close stdout the channel
                break

        stdout.close() # close stdout pseudo file
        stderr.close() # close stderr pseudo file

        if file:
            file.write("".join(self._output))
        return "".join(self._output), channel.recv_exit_status()
