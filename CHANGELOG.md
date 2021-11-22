# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2021-11-22

- Removed 'hostname' argument for `load_ssh_config` method in `SSHConfigData`.

## [0.1.0] - 2021-09-22

- Refactored `ssh2core.ssh_connect` to `ssh2core.sshconnect` (DEPRECATED: `ssh2core.ssh_connect`)
- Added `ssh2.core.SSHContext`
- Added `ssh2.core.SSHTunnelContext`
- Created `ssh2.config.SSHConfigData` to hold configuration properties for the SSH connection

## [0.0.1-dev0] - 2021-08-05

- Initial release (new project)