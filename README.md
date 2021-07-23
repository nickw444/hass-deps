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

## Why not HACS?
TODO

