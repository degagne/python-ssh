##########
Python-SSH
##########

Welcome to Python-SSH's documentation.

The purpose of ``Python-SSH`` was to provide a convenient and easy-to-user interface for interacting with remote hosts. 
It makes use of the `paramiko <https://www.paramiko.org/>`_ framework to establish SSH connections either directly or 
through tunnels to execute commands over SSH or SFTP.

============
Installation
============

To get started with ``Python-SSH``, install the latest stable release via `pip <https://pip.pypa.io/en/stable/>`_:

.. code-block:: bash
    :caption: Bash

    pip install python-ssh

``Python-SSH`` currently supports Python 3.6+ and relies on the following dependencies:

- `paramiko <https://www.paramiko.org/>`_
- `rich <https://rich.readthedocs.io/en/stable/index.html>`_

=====
Guide
=====

.. toctree::
    :maxdepth: 2

    Quickstart <quickstart>
    API Reference </apidoc/modules>

========
Releases
========

Releases are listed at https://github.com/degagne/python-ssh/releases

=======
License
=======

Python-SSH is licensed under MIT license. See the `LICENSE <https://github.com/degagne/python-ssh/blob/main/LICENSE>`_ 
for more information.

