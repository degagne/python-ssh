import copy
import pathlib
import paramiko
import typing as t

from dataclasses import dataclass
from paramiko import SSHConfig
from paramiko.config import SSHConfigDict
from paramiko.config import SSH_PORT
from paramiko import RejectPolicy
from ssh2.errors import SSHConfigurationError
from ssh2.constants import (
    SSH_CONFIG,
    INTEGER,
    BOOLEAN,
    SOCKS,
    CONFIG_KEY_MAPPING
)


@dataclass
class SSHConfigData:
    """
    :key hostname: The remote server to connect to.
    :key port: The remote server port to connect to, defaults to 22.
    :key username: The username to authenticate as.
    :key password: The password to authenticate with.
    :key key_filename: filename string (or list of filename strings) 
        of optional private key(s) and/or certs to try for authentication.
    :key timeout: An optional timeout (in seconds) for the 
        TCP connection.
    :key allow_agent: Enables/disables connecting to the SSH agent, 
        defaults to True.
    :key look_for_keys: Enables/disables searching for discoverable 
        private key files in :code:`~/.ssh/`, defaults to True.
    :key compress: Enables/disables compressions, defaults to False.
    :key sock: A socket or socket-like object to use for communication 
        to the target host.
    :key gss_auth: Enables/disables GSS-API authentication, defaults to False.
    :key gss_kex: Enables/disables GSS-API key exchange and user 
        authentication, defaults to False.
    :key gss_deleg_creds: Enables/disables delegatation of GSS-API 
        client credentials, defaults to True.
    :key gss_host: The targets name in the Kerberos database, defaults 
        to None.
    :key gss_trust_dns: Indicates whether or not the DNS is trusted to 
        securely canonicalize the name of the host being connected to, 
        defaults to True.
    :key banner_timeout: An optional timeout (in seconds) to wait for 
        the SSH banner to be presented.
    :key auth_timeout: An optional timeout (in seconds) to wait for an 
        authentication response.
    :key passphrase: Used for decrypting private keys.
    :key disabled_algorithms: An optional dictionary passed directly 
        to :code:`paramiko.Transport` and its keyword argument of the 
        same name.
    :key use_ssh_config: Enables/disables reading the SSH configuration 
        file.
    :key host_key_policy: Indicates which SSH client or key policy to 
        use, defaults to `paramiko.RejectPolicy`.
    :key host_key_file: Host key file to read, defaults to None.
    """
    hostname: str
    port: int = SSH_PORT
    username: str = None
    password: str = None
    key_filename: str = None
    timeout: int = None
    allow_agent: bool = True
    look_for_keys: bool = True
    compress: bool = False
    sock: t.Any = None
    gss_auth: bool = False
    gss_kex: bool = False
    gss_deleg_creds: bool = True
    gss_host: str = None
    gss_trust_dns: bool = True
    banner_timeout: int = None
    auth_timeout: int = None
    passphrase: str = None
    disabled_algorithms: str = None

    # Non SSH configuration properties.
    use_ssh_config: bool = True
    host_key_policy: t.Callable = RejectPolicy
    host_key_file: str = None

    def __post_init__(self):
        if self.use_ssh_config:
            configs = copy.copy(self.__dict__)
            configs.update(self.load_ssh_config(self.hostname))
            self.__dict__.update({k: v for k, v in configs.items()})

    def __iter__(self):
        for k, v in self.__dict__.items():
            if k not in ["use_ssh_config", "host_key_policy", "host_key_file"]:
                yield k, v

    @classmethod
    def load_ssh_config(
        cls,
        hostname: str,
        config_file: t.Optional[str] = SSH_CONFIG
    ) -> dict:
        """
        Loads SSH configuration properties.

        Generates a dict with supported keyword/values from the ssh_config 
        directives.

        :param str hostname: The remote server to connect to.
        :param str config_file: The filename for the ssh_config. 
            Default: ``~/.ssh/config``
        :return: A dict object with supported SSH configuration properties.
        :raises: ssh2.errors.SSHConfigurationError
        """
        config_file = pathlib.Path(config_file).expanduser()
        if not config_file.exists():
            raise SSHConfigurationError(
                f"SSH configuration file '{config_file}' cannot be found.")

        configs_dict = SSHConfigDict()
        ssh_config = SSHConfig.from_path(config_file).lookup(hostname)

        for (key, value, value_type) in CONFIG_KEY_MAPPING:
            if key in ssh_config:
                configs_dict.update({value: ssh_config[key]})
                if value_type == INTEGER:
                    configs_dict.update({value: configs_dict.as_int(value)})
                if value_type == BOOLEAN:
                    configs_dict.update({value: configs_dict.as_bool(value)})
                if value_type == SOCKS:
                    configs_dict.update(
                        {value: paramiko.ProxyCommand(ssh_config[key])})

        return configs_dict