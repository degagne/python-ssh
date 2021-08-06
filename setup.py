import os
import imp

import setuptools

version = imp.load_source("ssh2.version", os.path.join("ssh2", "version.py")).version


setuptools.setup(
    name="python-ssh",
    version=version,
    packages=setuptools.find_packages(include=["ssh2", "ssh2.*"]),
    package_dir={"ssh2": "ssh2"},
    license="MIT",
    author="Deric Degagne",
    author_email="deric.degagne@gmail.com",
    description="A library to execute commands on remote hosts.",
    url="https://github.com/degagne/python-ssh",
    project_urls={
        "Bug Tracker": "https://github.com/degagne/python-ssh/issues",
        "Documentation": "https://python-ssh.readthedocs.io/en/latest/index.html"
    },
    install_requires=[
        "paramiko",
        "rich"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)