import glob
import os
import subprocess
import tempfile
from typing import List, Optional, Any

from .dependency import Dependency


def find_source_artifacts(
    cloned_path: str,
    filename_hint: Optional[str] = None,
    filename: Optional[str] = None,
) -> List[str]:
    artifacts = []
    for artifact in glob.glob(
        os.path.join(cloned_path, "**/{}".format(filename_hint)), recursive=True
    ):
        artifacts.append(artifact)

    return artifacts


def checkout_dependency_source(
    dependency: Dependency, ref: Optional[str] = None
) -> tempfile.TemporaryDirectory[Any]:
    tmpdir = tempfile.TemporaryDirectory(suffix="-" + dependency.get_name())
    subprocess.run(
        ["git", "clone", dependency.source, tmpdir.name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if ref is not None:
        subprocess.run(
            ["git", "checkout", ref],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=tmpdir.name,
        )

    return tmpdir
