from typing import Any, Dict, Optional
from dataclasses import InitVar, dataclass

from gcip.core.job import Job


@dataclass(kw_only=True)
class Flake8(Job):
    """
    Runs:

    ```
    pip3 install --upgrade flake8
    flake8
    ```

    This subclass of `Job` will configure following defaults for the superclass:

    * name: flake8
    * stage: lint
    """

    jobName: InitVar[str] = "flake8"
    jobStage: InitVar[str] = "lint"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            "pip3 install --upgrade flake8",
            "flake8",
        ]
        return super().render()


@dataclass(kw_only=True)
class Mypy(Job):
    """
    Install mypy if not already installed.
    Execute mypy for `package_dir`.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: mypy
    * stage: lint

    Args:
        package_dir (str): Package directory to type check.
        mypy_version (str, optional): If `mypy` is not already installed, this version will be installed. Defaults to
            'latest' (unset). Must be only the verion number, e.g. '1.2.3'.
        mypy_options (Optional[str], optional): Adds arguments to mypy execution. Defaults to None.
    Returns:
        Job: gcip.Job
    """

    package_dir: str
    mypy_version: Optional[str] = None
    mypy_options: Optional[str] = None
    jobName: InitVar[str] = "mypy"
    jobStage: InitVar[str] = "lint"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:

        mypy_version_identifier = ""
        if self.mypy_version:
            mypy_version_identifier = f"=={self.mypy_version}"
        self._scripts = [
            f'pip3 freeze | grep -q "^mypy" || pip3 install mypy{mypy_version_identifier}',
            f"yes | mypy --install-types {self.package_dir} || true",
        ]

        if self.mypy_options:
            self._scripts.append(f"mypy {self.mypy_options} {self.package_dir}")
        else:
            self._scripts.append(f"mypy {self.package_dir}")

        return super().render()


@dataclass(kw_only=True)
class Isort(Job):
    """
    Runs:

    ```
    pip3 install --upgrade isort
    isort --check .
    ```

    This subclass of `Job` will configure following defaults for the superclass:

    * name: isort
    * stage: lint
    """

    jobName: InitVar[str] = "isort"
    jobStage: InitVar[str] = "lint"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            "pip3 install --upgrade isort",
            "isort --check .",
        ]
        return super().render()
