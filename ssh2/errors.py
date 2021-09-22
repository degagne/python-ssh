class SSHConfigurationError(RuntimeError):
    """
    Exception raised when one or more unsupported SSH configuration 
    properties are invoked.
    """
    pass


class SSHConnectionError(RuntimeError):
    """
    Exception raised when a connection to remote host fails.
    """
    pass


class SSHChannelError(SSHConnectionError):
    """
    Exception raised when ``paramiko.open_channel`` fails to create a 
    socket object for our tunnel.
    """
    pass


class SFTPError(SSHConnectionError):
    """
    Exception raised when an ``SSHClient`` object doesn't exist and the 
    user attempts to create a new ``SFTPClient`` session object.
    """
    pass


class SSHContextError(SSHConnectionError):
    """
    Exception raised when the SSH context cannot be created.
    """
    pass