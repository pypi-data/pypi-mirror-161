from typing import Any, Dict
from dataclasses import InitVar, dataclass

from gcip.core.job import Job
from gcip.addons.python.scripts import (
    pip_install_requirements,
)
from gcip.addons.linux.scripts.package_manager import (
    install_packages,
)


@dataclass(kw_only=True)
class BdistWheel(Job):
    """
    Runs `python3 setup.py bdist_wheel` and installs project requirements
    before (`scripts.pip_install_requirements()`)

    * Requires a `requirements.txt` in your project folder containing at least `setuptools`
    * Creates artifacts under the path `dist/`

    This subclass of `Job` will configure following defaults for the superclass:

    * name: bdist_wheel
    * stage: build
    * artifacts: Path 'dist/'
    """

    jobName: InitVar[str] = "bdist_wheel"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.artifacts.add_paths("dist/")

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            pip_install_requirements(),
            "pip list | grep setuptools-git-versioning && " + install_packages("git"),
            "python3 setup.py bdist_wheel",
        ]
        return super().render()
