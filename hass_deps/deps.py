from typing import Optional

import click

from .dependency import Dependency, LockedDependency, load_package_info
from .deps_core import (
    install_core_dependency,
    is_core_dependency,
    get_core_destination_path,
)
from .deps_lovelace import (
    install_lovelace_release_dependency,
    install_lovelace_dependency,
    get_lovelace_destination_path,
)
from .source import checkout_dependency_source


def install_dependency(
    config_root_path: str,
    dependency: Dependency,
    lock_info: Optional[LockedDependency],
    force: bool = False,
) -> LockedDependency:
    click.echo(click.style(f"Installing: {dependency.get_name()} ", fg="green"))

    if not force and lock_info is not None:
        if lock_info.type == "lovelace":
            installed_path = get_lovelace_destination_path(
                config_root_path, lock_info.get_name()
            )
            package_info = load_package_info(installed_path)
            if package_info is not None and package_info.version == lock_info.version:
                click.echo(
                    f"{dependency.get_name()}@{lock_info.version} already installed"
                )
                return lock_info

        elif lock_info.type == "core":
            if lock_info.components is None:
                raise Exception("Expected components to be defined")

            for component in lock_info.components:
                installed_path = get_core_destination_path(config_root_path, component)
                package_info = load_package_info(installed_path)
                if package_info is None or package_info.version != lock_info.version:
                    # Installed version != locked version, reinstall.
                    break
            else:  # nobreak
                click.echo(
                    f"{dependency.get_name()}@{lock_info.version} already installed"
                )
                return lock_info
        else:
            raise AssertionError("Unknown locked dependency type: " + lock_info.type)

    if lock_info is not None and lock_info.type == "lovelace" and lock_info.is_release:
        # Install directly from Github Releases, skip inference logic.
        rv = install_lovelace_release_dependency(
            config_root_path, dependency, tag_name=lock_info.version
        )
    else:
        version_ref = lock_info.version if lock_info else None
        with checkout_dependency_source(dependency, version_ref) as source_path:
            is_core = (
                lock_info.type == "core"
                if lock_info
                else is_core_dependency(dependency, source_path)
            )
            if is_core:
                rv = install_core_dependency(config_root_path, dependency, source_path)
            else:
                rv = install_lovelace_dependency(
                    config_root_path, dependency, source_path
                )

    click.echo(f"Installed {dependency.get_name()}@{rv.version}")
    return rv
