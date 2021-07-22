import json
import os
from collections import OrderedDict
from hashlib import sha1
from os.path import basename, splitext
from typing import List, NamedTuple, Literal
from typing import Optional
from urllib.parse import urlparse

from ruamel.yaml import YAML

yaml = YAML()


class Dependency(NamedTuple):
    source: str
    root_is_custom_components: bool
    include: Optional[List[str]]

    def get_name(self):
        name, _ = splitext(basename(urlparse(self.source).path))
        return name

    def get_src_hash(self):
        return sha1(self.source.encode('utf8')).hexdigest()[:8]

    def is_github(self):
        return urlparse(self.source).hostname == 'github.com'

    def get_github_slug(self):
        parsed = urlparse(self.source)
        if parsed.hostname == 'github.com':
            return parsed.path[1:].rstrip('.git')


class LockedDependency(NamedTuple):
    source: str
    version: str
    is_release: bool
    type: Literal['core', 'lovelace']
    # List of installed core components from this dependency
    # (only applicable when type is core)
    components: Optional[List[str]]

    def get_name(self):
        name, _ = splitext(basename(urlparse(self.source).path))
        return name

def load_dependencies(path: str) -> OrderedDict[str, Dependency]:
    dependencies = OrderedDict()
    with open(path) as f:
        for dep in yaml.load(f)['dependencies']:
            if isinstance(dep, str):
                dep = {'source': dep}
            dependencies[dep['source']] = Dependency(
                source=dep['source'],
                root_is_custom_components=dep.get(
                    'root_is_custom_components', False),
                include=dep.get('include'),
            )
    return dependencies


def write_dependencies(path: str, dependencies: OrderedDict[str, Dependency]):
    dumpable = []
    for source, dependency in dependencies.items():
        dumpable_dep = dependency.source

        if dependency.include is not None or dependency.root_is_custom_components:
            # Has more advanced config, dump as an object
            dumpable_dep = {'source': dependency.source}
            if dependency.root_is_custom_components:
                dumpable_dep['root_is_custom_components'] = True
            if dependency.include is not None:
                dumpable_dep['include'] = dependency.include

        dumpable.append(dumpable_dep)

    with open(path, 'w') as f:
        yaml.dump({
            'dependencies': dumpable,
        }, f)


def load_locked_dependencies(path: str) -> OrderedDict[str, LockedDependency]:
    dependencies = OrderedDict()
    with open(path) as f:
        for source, data in yaml.load(f).items():
            dependencies[source] = LockedDependency(
                source=source,
                version=data['version'],
                is_release=data.get('is_release', False),
                type=data['type'],
                components=data.get('components'),
            )
    return dependencies


def write_locked_dependencies(path: str, locked_dependencies: OrderedDict[
    str, LockedDependency]):
    dumpable = {}
    for source, lock_info in locked_dependencies.items():
        dumpable[source] = {
            'version': lock_info.version,
            'type': lock_info.type,
        }

        if lock_info.is_release:
            dumpable[source]['is_release'] = True

        if lock_info.components is not None:
            dumpable[source]['components'] = lock_info.components

    with open(path, 'w') as f:
        yaml.dump(dumpable, f)


class PackageInfo(NamedTuple):
    version: str


def load_package_info(package_dir: str) -> Optional[PackageInfo]:
    package_info_path = os.path.join(package_dir, '.hass-deps')
    if not os.path.exists(package_info_path):
        return

    with open(package_info_path) as f:
        data = json.load(f)
        return PackageInfo(
            version=data['version']
        )


def write_package_info(package_dir: str, info: PackageInfo):
    with open(os.path.join(package_dir, '.hass-deps'), 'w') as f:
        json.dump({
            'version': info.version
        }, f)
