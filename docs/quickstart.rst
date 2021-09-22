##########
Quickstart
##########

This guide will walk you through the basics of how to create SSH connections,
with and/or without tunnels, and open SFTP sessions.

==================
Connection Methods
==================

In order to establish a SSH connection to a remote host, user's can use one 
of the following 3 methods:

1. :ref:`Direct Connection`
2. :ref:`Decorated Connection`
3. :ref:`Context Connection` 

.. seealso::

    For a full reference on the available configuration properties, see the 
    :class:`ssh2.config.SSHConfigData`.

Direct Connection
-----------------

A **direct connection**, instantiates a new :class:`ssh2.SSH`, by invoking 
the :class:`ssh2.SSH` directly.

.. literalinclude:: ../examples/ssh.py
  :language: python

Decorated Connection
--------------------

A **decorated connection**, instantiates a new :class:`ssh2.SSH`, by invoking 
the :class:`ssh2.core.SSHConnect` object. Invocation of this object will 
automatically include the :class:`ssh2.SSH` object into the decorated 
function.

For examples, please see `SSHConnect <examples.html#ssh2-sshconnect>`_

.. literalinclude:: ../examples/sshconnect.py
  :language: python

Context Connection
------------------

A **context connection**, instantiates a new :class:`ssh2.SSH`, by invoking 
the :class:`ssh2.core.SSHContext` object.

.. literalinclude:: ../examples/sshcontext.py
  :language: python

Also, available within the **context connection**, is the 
:class:`ssh2.core.SSHTunnelContext`. Similarly, to the 
:class:`ssh2.core.SSHContext`, this instantiates a new :class:`ssh2.SSH`, 
but through a tunnel connection using a jumphost. It's recommended to 
configure the :code:`ProxyCommand` directive within your SSH configuration 
file, however, this provides the same functionality.

.. literalinclude:: ../examples/sshtunnelcontext.py
  :language: python

===============
SFTP Connection
===============

To initiate an SFTP session, create a new :class:`ssh2.SSH`, the open the SFTP
session with :class:`ssh2.SSH.open_sftp`.

.. literalinclude:: ../examples/sftp.py
  :language: python
