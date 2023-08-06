# rettij router component

## Requirements

There are currently no known requirements to use this component.

## Usage

### Configuration

Currently, FRR is configured via the integrated ``frr.conf`` configuration file rather than the daemon-specific files.

Please refer to the official documentation at https://docs.frrouting.org/en/latest/ to learn about the available commands and settings.

#### Startup configuration via configuration file

In order to add a configuration to be loaded at startup, create a folder (or folder structure) inside the ``user/config/`` directory and add the folder path relative to ``config`` to the node in the topology under ``config`` -> ``config-dir``.

````
# Example folder structure
<project-root>/user/config/frr/router1/user.conf

# Example topology excerpt
  - id: router1
    device: router
    component: simple-router
    [...]
    config:
      config-dir: frr/test_router1
````

These files will be copied to the node after startup and appended to the integrated initial configuration, which contains the hostname, SNMP settings and other pre-configured settings. After the new configuration instructions have been added, the complete configuration is applied.

#### Configuration during runtime via configuration file
In order to update the running configuration via config file, you need to run the ``UpdateRouterConfigFileCommand`` with the absolute path to the config file.

**IMPORTANT:** Running this method completely overwrites the existing configuration! You may want to first export the current configuration using the ``DownloadRouterConfigFileCommand`` and manually integrate new changes.

Before the update is made, the current running config is backed up.

#### Configuration during run via single commands
In oder to update the running configuration via CLI command(s), you need to run the ``ExecuteRouterConfigCommand`` with a list of commands. Also you can optionally specify a daemon to set the commands for.

**IMPORTANT:** This only changes the runtime config. All changes made this way are lost during reboot.