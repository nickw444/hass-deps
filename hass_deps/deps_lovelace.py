import json
import os
import shutil
import subprocess
from typing import Optional, Dict, Any, cast, List
from urllib.parse import urlparse

import requests

from .dependency import Dependency, LockedDependency, PackageInfo, write_package_info
from .exceptions import ArtifactNotFoundException
from .source import find_source_artifacts


def get_github_release(
    dependency: Dependency, tag_name: Optional[str]
) -> Optional[Dict[str, Any]]:
    github_slug = dependency.get_github_slug()
    if github_slug is None:
        # Cannot check Github if the dependency doesn't come from Github!
        return None

    url = f"https://api.github.com/repos/{github_slug}/releases/latest"
    if tag_name is not None:
        url = f"https://api.github.com/repos/{github_slug}/releases/tags/{tag_name}"

    resp = requests.get(url)
    resp.raise_for_status()
    return cast(Dict[str, Any], resp.json())


def find_github_releases_artifacts(
    dependency: Dependency, release_data: Dict[str, Any]
) -> List[str]:
    artifacts = []
    for asset in release_data["assets"]:
        if asset["name"].endswith(".js") or asset["name"].endswith(".map"):
            artifacts.append(asset["browser_download_url"])

    return artifacts


def get_lovelace_destination_path(config_root_path: str, name: str) -> str:
    return os.path.join(config_root_path, "www/community", name)


def install_lovelace_release_dependency(
    config_root_path: str, dependency: Dependency, tag_name: Optional[str]
) -> LockedDependency:
    release_data = get_github_release(dependency, tag_name=tag_name)
    if release_data is None:
        raise ArtifactNotFoundException()

    github_artifacts = find_github_releases_artifacts(dependency, release_data)
    if len(github_artifacts):
        destination_path = get_lovelace_destination_path(
            config_root_path, dependency.get_name()
        )
        if os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        os.makedirs(destination_path, exist_ok=True)

        for artifact in github_artifacts:
            artifact_basename = os.path.basename(urlparse(artifact).path)
            artifact_destination_path = os.path.join(
                destination_path, artifact_basename
            )
            resp = requests.get(artifact)
            resp.raise_for_status()
            with open(artifact_destination_path, "wb") as f:
                f.write(resp.content)

        version = release_data["tag_name"]
        write_package_info(destination_path, PackageInfo(version=version))

        return LockedDependency(
            source=dependency.source,
            version=version,
            is_release=True,
            type="lovelace",
            components=None,
        )

    raise ArtifactNotFoundException()


def install_lovelace_dependency(
    config_root_path: str,
    dependency: Dependency,
    cloned_path: str,
) -> LockedDependency:
    hacs_json_path = os.path.join(cloned_path, "hacs.json")
    source_artifacts = []
    if dependency.assets is not None:
        source_artifacts = [os.path.join(cloned_path, x) for x in dependency.assets]
    elif os.path.exists(hacs_json_path):
        hacs_config = json.load(open(hacs_json_path))

        if "filename" in hacs_config:
            source_artifacts = find_source_artifacts(
                cloned_path, filename_hint=hacs_config["filename"]
            )
        else:
            source_artifacts = find_source_artifacts(
                cloned_path, filename_hint=f"*{hacs_config['name']}*"
            )

        source_artifacts = list(
            filter(lambda x: x.endswith(".map") or x.endswith(".js"), source_artifacts)
        )

    if len(source_artifacts):
        destination_path = get_lovelace_destination_path(
            config_root_path, dependency.get_name()
        )
        if os.path.isdir(destination_path):
            shutil.rmtree(destination_path)
        os.makedirs(destination_path, exist_ok=True)

        for artifact in source_artifacts:
            artifact_basename = os.path.basename(artifact)
            artifact_destination_path = os.path.join(
                destination_path, artifact_basename
            )
            shutil.copy(artifact, artifact_destination_path)

        describe_result = subprocess.run(
            ["git", "describe", "--always"], cwd=cloned_path, stdout=subprocess.PIPE
        )
        version = describe_result.stdout.decode("utf-8").strip()
        with open(os.path.join(destination_path, ".hass-deps"), "w") as f:
            json.dump({"version": version}, f)

        return LockedDependency(
            source=dependency.source,
            version=version,
            is_release=False,
            type="lovelace",
            components=None,
        )

    # No source candidates found, try check Github Releases.
    return install_lovelace_release_dependency(config_root_path, dependency, None)
