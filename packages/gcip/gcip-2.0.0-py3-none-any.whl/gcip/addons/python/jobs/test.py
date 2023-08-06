from typing import Any, Dict
from dataclasses import InitVar, dataclass

from gcip.lib import rules
from gcip.core.job import Job
from gcip.addons.python.scripts import (
    pip_install_requirements,
)
from gcip.addons.container.images import PredefinedImages


@dataclass(kw_only=True)
class Pytest(Job):
    """
    Runs `pytest` and installs project requirements before (`scripts.pip_install_requirements()`)

    * Requires a `requirements.txt` in your project folder containing at least `pytest`

    This subclass of `Job` will configure following defaults for the superclass:

    * name: pytest
    * stage: test

    Args:
        pytestCommand (str): This argument ist only required if you have a custom command
            to call pytest.
    """

    pytestCommand: str = "pytest"
    jobName: InitVar[str] = "pytest"
    jobStage: InitVar[str] = "test"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            pip_install_requirements(),
            self.pytestCommand,
        ]
        return super().render()


@dataclass(kw_only=True)
class EvaluateGitTagPep440Conformity(Job):
    """
    Checks if the current pipelines `$CI_COMMIT_TAG` validates to a valid Python package version according to
    https://www.python.org/dev/peps/pep-0440

    This job already contains a rule to only run when a `$CI_COMMIT_TAG` is present (`rules.only_tags()`).

    Runs `pytest` and installs project requirements before (`scripts.pip_install_requirements()`)

    * Requires a `requirements.txt` in your project folder containing at least `pytest`

    This subclass of `Job` will configure following defaults for the superclass:

    * name: tag-pep440-conformity
    * stage: test
    * image: PredefinedImages.GCIP
    * rules: on_tagsg
    """

    jobName: InitVar[str] = "tag-pep440-conformity"
    jobStage: InitVar[str] = "test"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.GCIP)
        self.append_rules(rules.on_tags())

    def render(self) -> Dict[str, Any]:
        self._scripts = ["python3 -m gcip.tools.evaluate_git_tag_pep440_conformity"]
        return super().render()
