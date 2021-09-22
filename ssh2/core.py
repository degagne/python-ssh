from __future__ import absolute_import

import typing as t

from threading import Lock
from ssh2 import SSH
from ssh2 import SSHConfigData


class SSHConnect:
    """
    Creates a new :class:`ssh2.SSH`` into the decorated method.
    
    This class supports all keys from :class:`ssh2.config.SSHConfigData`, 
    however, the ``hostname`` key must be provided. 
    """
    def __init__(self, **configs: dict) -> t.NoReturn:
        self.configs = SSHConfigData(**configs)

    def __call__(self, func: t.Callable, *args: list, **kwargs: dict):
        def inner(*args: list, **kwargs: dict):                
            try:
                ssh = SSH()
                ssh.connect(self.configs)
                return func(ssh, *args, **kwargs)
            finally:
                ssh.disconnect()
        return inner


class SSHContext(SSH):
    """
    Creates a new :class:`ssh2.SSH`` as a context.
    
    This class supports all keys from :class:`ssh2.config.SSHConfigData`, 
    however, the ``hostname`` key must be provided.
    """
    def __init__(self, **configs: dict) -> t.NoReturn:
        self._configs = SSHConfigData(**configs)
        self._init_lock = Lock()
        super().__init__()

    def __enter__(self):
        """
        Create SSH context.
        """
        self._init_lock.acquire()
        self.connect(self._configs)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close context.
        """
        try:
            self.disconnect()
        finally:
            self._init_lock.release()


class SSHTunnelContext(SSH):
    """
    Creates a new :class:`ssh2.SSH`` into the decorated method.
    
    This class supports all keys from :class:`ssh2.config.SSHConfigData`, 
    however, the ``hostname`` key must be provided. 
    
    Provides an interface to create a SSH connection through a tunnel to 
    an "unreachable" host. It's recommended that a tunnel should be 
    completed using the SSH configuration file (ProxyCommand), however
    for instances where that is not possible, this context will provide
    this functionality.

    :param tunnel_configs: :class:`ssh2.SSHConfigData` object with the
        tunnel configurations.
    :param configs: :class:`ssh2.SSHConfigData` object with the destination
        host configurations.
    """
    def __init__(
        self,
        tunnel_configs: SSHConfigData,
        configs: SSHConfigData
    ) -> t.NoReturn:
        self._tunnel_configs = tunnel_configs
        self._configs = configs
        self._init_lock = Lock()
        super().__init__()

    def _prepare_context(self):
        """
        Prepare SSH tunnel context.
        """
        sock = self.open_tunnel(self._tunnel_configs, self._configs.hostname)
        setattr(self._configs, "sock", sock)
        self.connect(self._configs)

    def __enter__(self):
        """
        Create SSH tunnel context.
        """
        self._init_lock.acquire()
        self._prepare_context()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close context.
        """
        try:
            self.disconnect()
        finally:
            self._init_lock.release()