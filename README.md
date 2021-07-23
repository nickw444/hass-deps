# hass-deps

An un-opinionated command line dependency manager for Home Assistant

## Installing

```sh
pip install hass-deps
```

## Usage

`hass-deps` can be invoked directly from the root of your Home Assistant configuration directory, however the config
directory can be specified via the `--config-dir` switch.

### Add a dependency

```sh
hass-deps add <dependency source>
```

**e.g.:**

```sh
hass-deps add https://github.com/nickw444/deebot-t8-hass.git
```

### Install/sync all dependencies

Ensures the local dependencies are in-sync with those defined in the lock file.

```sh
hass-deps install
```

To force reinstallation of dependencies even where installed version matches the lock file version, use the `--force`
switch:

```sh
hass-deps install --force
```

### Upgrade a dependency

**Upgrading a single dependency to the latest version:**

```sh
hass-deps upgrade <dependency source>
```

**Upgrading all dependencies to the latest version:**

```sh
hass-deps upgrade
```

## Why not [HACS](https://hacs.xyz/)?

[HACS](https://hacs.xyz/) is a great plugin for Home Assistant, particularly for less tech-savvy users who might not be familiar connecting to a remote machine via SSH or Samba to install a new dependency. 

From my limited time using HACS I was disapointed there was no way to "check in" the set of installed dependencies, other than taking a snapshot of the Home Assistant configuration.

Due to this, my config validation pipeline in CI failed (as it had no way to know which dependencies were installed). 

Furthermore, the recent security advisory for HACS came to light, which further made me consider whether I wanted such a fully functional addon part of my Home Assistant environment. 

Using `hass-deps`, references to your dependencies can be checked in to version control, and reinstalled in a reproducible (due to the lockfile functionality in `hass-heps`)
