import os
from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable, List

import click

from .dependency import (
    Dependency, LockedDependency,
    write_locked_dependencies, write_dependencies, load_locked_dependencies,
    load_dependencies)
from .deps import install_dependency


@dataclass
class TypedObj:
    config_dir: str
    dependencies: OrderedDict[str, Dependency]
    locked_dependencies: OrderedDict[str, LockedDependency]

    write_dependencies: Callable[[], None]
    write_locked_dependencies: Callable[[], None]


@click.group()
@click.pass_context
@click.option('--config-dir', type=click.Path(exists=True), default='./')
def cli(ctx, config_dir: str):
    dependencies_path = os.path.join(config_dir, "hass-deps.yaml")
    dependencies_lock_path = os.path.join(config_dir, "hass-deps.lock")

    dependencies = OrderedDict()
    if os.path.exists(dependencies_path):
        dependencies = load_dependencies(dependencies_path)

    locked_dependencies = OrderedDict()
    if os.path.exists(dependencies_lock_path):
        locked_dependencies = load_locked_dependencies(dependencies_lock_path)

    def write_dependencies_():
        write_dependencies(
            dependencies_path, ctx.obj.dependencies)

    def write_locked_dependencies_():
        write_locked_dependencies(
            dependencies_lock_path, ctx.obj.locked_dependencies)

    ctx.obj = TypedObj(
        config_dir=config_dir,
        dependencies=dependencies,
        locked_dependencies=locked_dependencies,
        write_dependencies=write_dependencies_,
        write_locked_dependencies=write_locked_dependencies_
    )


@cli.command(help="Add a new dependency")
@click.pass_obj
@click.argument("dependency")
def add(obj: TypedObj, dependency: str):
    dep = Dependency(
        source=dependency,
        root_is_custom_components=False,
        include=None
    )
    lock_info = install_dependency(obj.config_dir, dep, lock_info=None)

    obj.dependencies[dependency] = dep
    obj.locked_dependencies[dependency] = lock_info

    obj.write_dependencies()
    obj.write_locked_dependencies()


@cli.command(help="Install dependencies from hass-deps.yaml")
@click.pass_obj
@click.option('--force', help="Force reinstallation of all dependencies",
              default=False, is_flag=True)
def install(obj: TypedObj, force: bool):
    should_write_locked_dependencies = False

    for dependency in obj.dependencies.values():
        lock_info = obj.locked_dependencies.get(dependency.source)
        updated_lock_info = install_dependency(
            obj.config_dir, dependency, lock_info, force=force)

        if lock_info is None:
            # Only update locked dependency if no lock was previously specified
            should_write_locked_dependencies = True
            obj.locked_dependencies[dependency.source] = updated_lock_info

    if should_write_locked_dependencies:
        obj.write_locked_dependencies()


@cli.command(help="Upgrade dependencies to the latest version/release")
@click.pass_obj
@click.argument('dependencies', nargs=-1, metavar='dependency')
def upgrade(obj: TypedObj, dependencies: List[str]):
    if len(dependencies) == 0:
        # No dependencies specified, upgrade all!
        dependencies = obj.dependencies.keys()

    for dep_source in dependencies:
        # TODO: Eagerly error for non installed dependency in list.
        dep = obj.dependencies[dep_source]
        lock_info = install_dependency(obj.config_dir, dep, lock_info=None)
        obj.locked_dependencies[dep_source] = lock_info

    obj.write_locked_dependencies()


if __name__ == '__main__':
    cli()
