__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Daniel von Eßen"
__email__ = "daniel.von-essen@deutschebahn.com"

from os import path
from typing import Any, Dict, Optional
from dataclasses import InitVar, dataclass

from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.images import PredefinedImages


def _is_float_between_zero_and_one(validate: float) -> bool:
    """
    Helper function to validate given arguments type and range.

    If `validate` is not of type float or not between 0.0 and 1.0 function returns `False`.
            Otherwise function returns `True`
    Args:
        validate (float): Argument to validate.

    Returns:
        bool:
    """

    if not isinstance(validate, float):
        raise TypeError("Argument is not of type float.")
    if not 0 <= validate <= 1:
        raise ValueError("Argument is not between 0.0 and 1.0.")
    return True


@dataclass(kw_only=True)
class Scan(Job):
    """
    Scan your images with [wagoodman/dive](https://github.com/wagoodman/dive).

    `dive` will scan your container image layers and will output the efficency of each layer.
    You can see which layer and which file is consuming the most storage and optimize the layers if possible.
    It prevents container images and its layers beeing polluted with files like apt or yum cache's.
    The output produced by `dive` is uploaded as an artifact to the GitLab instance.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: dive
    * stage: check
    * image: PredefinedImages.DIVE
    * artifacts: Path 'dive.txt'

    Args:
        image_path (Optional[str]): Path to the image can be either a remote container registry,
            as well as a local path to an image. Defaults to `PredefinedVariables.CI_PROJECT_PATH`.
        image_name (Optional[str]): Name of the container image to scan, if `source` is `docker-archive` argument gets prefix `.tar`.
            Defaults to PredefinedVariables.CI_PROJECT_NAME.
        highest_user_wasted_percent (Optional[float]): Highest allowable percentage of bytes wasted
            (as a ratio between 0-1), otherwise CI validation will fail. (default "0.1"). Defaults to None.
        highest_wasted_bytes (Optional[float]): Highest allowable bytes wasted, otherwise CI validation will fail.
            (default "disabled"). Defaults to None.
        lowest_efficiency (Optional[float]): Lowest allowable image efficiency (as a ratio between 0-1),
            otherwise CI validation will fail. (default "0.9"). Defaults to None.
        ignore_errors (Optional[bool]): Ignore image parsing errors and run the analysis anyway. Defaults to False.
        source (Optional[str]): The container engine to fetch the image from. Allowed values: docker, podman, docker-archive
            (default "docker"). Defaults to "docker-archive".
    """

    image_path: str = "/" + PredefinedVariables.CI_PROJECT_PATH
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    highest_user_wasted_percent: Optional[float] = None
    highest_wasted_bytes: Optional[float] = None
    lowest_efficiency: Optional[float] = None
    ignore_errors: bool = False
    source: str = "docker-archive"
    jobName: InitVar[str] = "dive"
    jobStage: InitVar[str] = "check"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.DIVE)
        self.artifacts.add_paths("dive.txt")

    def render(self) -> Dict[str, Any]:
        if self.image_path.endswith("/"):
            self.image_path = self.image_path[:-1]

        if self.source == "docker-archive":
            self.image_name = f"{self.image_name}.tar".replace("/", "_")

        dive_command = ["dive", f"{self.source}://{self.image_path}/{self.image_name}", "--ci"]

        if self.highest_user_wasted_percent and _is_float_between_zero_and_one(self.highest_user_wasted_percent):
            dive_command.append(f'--highestUserWastedPercent "{self.highest_user_wasted_percent}"')
        if self.highest_wasted_bytes and _is_float_between_zero_and_one(self.highest_wasted_bytes):
            dive_command.append(f'--highestWastedBytes "{self.highest_wasted_bytes}"')
        if self.lowest_efficiency and _is_float_between_zero_and_one(self.lowest_efficiency):
            dive_command.append(f'--lowestEfficiency "{self.lowest_efficiency}"')
        if self.ignore_errors:
            dive_command.append("--ignore-errors")

        dive_command.append("|tee " + path.join(PredefinedVariables.CI_PROJECT_DIR, "dive.txt"))

        self._scripts = [
            "set -eo pipefail",
            " ".join(dive_command),
        ]

        return super().render()
