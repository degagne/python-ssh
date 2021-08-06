from __future__ import absolute_import

import typing as t

from ssh2 import SSH


class ssh_connect(SSH):
    """Instantiates the ``SSH`` object.

    Provides the interface for SSH connections to remote hosts. Inherites all
    public methods from the ``SSH`` object.
    """
    def __call__(self, func: t.Callable, *args: t.List[t.Any], **kwargs: t.Dict[str, t.Any]):
        def inner_func(*args: t.List[t.Any], **kwargs: t.Dict[str, t.Any]):
            try:
                return func(self, *args, **kwargs)
            finally:
                self.disconnect() # close socket connection to remote host
        return inner_func