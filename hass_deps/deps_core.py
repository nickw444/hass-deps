import json
import os
import shutil
import subprocess

from .dependency import Dependency, LockedDependency
from .exceptions import ArtifactNotFoundException


def is_core_dependency(dependency: Dependency, cloned_path: str) -> bool:
    custom_components_path = os.path.join(cloned_path, "custom_components")
    if dependency.root_is_custom_components:
        custom_components_path = cloned_path

    return os.path.exists(custom_components_path)


def get_core_destination_path(config_root_path: str, name: str) -> str:
    return os.path.join(config_root_path, "custom_components", name)


def install_core_dependency(
    config_root_path: str, dependency: Dependency, cloned_path: str
) -> LockedDependency:
    custom_components_path = os.path.join(cloned_path, "custom_components")
    if dependency.root_is_custom_components:
        custom_components_path = cloned_path

    if not os.path.exists(custom_components_path):
        raise ArtifactNotFoundException()

    custom_components_root_path = os.path.join(config_root_path, "custom_components")
    if not os.path.exists(custom_components_root_path):
        os.mkdir(custom_components_root_path)

    describe_result = subprocess.run(
        ["git", "describe", "--always"], cwd=cloned_path, stdout=subprocess.PIPE
    )
    version = describe_result.stdout.decode("utf-8").strip()

    installed_components = []
    for component in os.listdir(custom_components_path):
        component_path = os.path.join(custom_components_path, component)
        if component.startswith(".") or not os.path.isdir(component_path):
            continue

        if dependency.include is not None and component not in dependency.include:
            continue

        destination_path = get_core_destination_path(config_root_path, component)
        if os.path.exists(destination_path):
            shutil.rmtree(destination_path)

        shutil.copytree(component_path, destination_path)
        installed_components.append(component)

        with open(os.path.join(destination_path, ".hass-deps"), "w") as f:
            json.dump({"version": version}, f)

    return LockedDependency(
        source=dependency.source,
        version=version,
        is_release=False,
        type="core",
        components=installed_components,
    )
