import glob
import os
import subprocess
import tempfile
from typing import Literal

from .dependency import Dependency


def find_source_artifacts(cloned_path: str,
                          filename_hint: str = None,
                          filename: str = None):
    artifacts = []
    for artifact in glob.glob(
            os.path.join(cloned_path, '**/{}'.format(filename_hint)),
            recursive=True):
        artifacts.append(artifact)

    return artifacts


def checkout_dependency_source(dependency: Dependency, ref: str = None):
    tmpdir = tempfile.TemporaryDirectory(suffix='-' + dependency.get_name())
    subprocess.run(
        ['git', 'clone', dependency.source, tmpdir.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    if ref is not None:
        subprocess.run(
            ['git', 'checkout', ref],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmpdir.name)

    return tmpdir


def get_destination_path(config_root_path: str, dependency_name: str,
                         dependency_type: Literal['lovelace', 'core']):
    if dependency_type == 'lovelace':
        directory = 'www'
    elif dependency_type == 'core':
        directory = 'custom_components'
    else:
        raise AssertionError()

    return os.path.join(config_root_path, directory, dependency_name)
