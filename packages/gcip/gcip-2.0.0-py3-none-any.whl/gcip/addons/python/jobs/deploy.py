from typing import Any, Dict, Optional
from dataclasses import InitVar, dataclass

from gcip.core.job import Job


@dataclass(kw_only=True)
class TwineUpload(Job):
    """
    Runs:

    ```
    pip3 install --upgrade twine
    python3 -m twine upload --non-interactive --disable-progress-bar dist/*
    ```

    * Requires artifacts from a build job under `dist/` (e.g. from `bdist_wheel()`)

    This subclass of `Job` will configure following defaults for the superclass:

    * name: twine
    * stage: deploy

    Args:
        twine_repository_url (str): The URL to the PyPI repository the python artifacts will be deployed to. Defaults
            to `None`, which means the package is published to `https://pypi.org`.
        twine_username_env_var (Optional[str]): The name of the environment variable, which contains the username value.
            **DO NOT PROVIDE THE USERNAME VALUE ITSELF!** This would be a security issue! Defaults to `TWINE_USERNAME`.
        twine_password_env_var (Optional[str]): The name of the environment variable, which contains the password.
            **DO NOT PROVIDE THE LOGIN VALUE ITSELF!** This would be a security issue! Defaults to `TWINE_PASSWORD`.
    """

    twine_repository_url: Optional[str] = None
    twine_username_env_var: Optional[str] = "TWINE_USERNAME"
    twine_password_env_var: Optional[str] = "TWINE_PASSWORD"
    jobName: InitVar[str] = "twine"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:

        self.add_variables(
            TWINE_USERNAME=f"${self.twine_username_env_var}",
            TWINE_PASSWORD=f"${self.twine_password_env_var}",
        )

        if self.twine_repository_url:
            self.add_variables(TWINE_REPOSITORY_URL=self.twine_repository_url)

        self._scripts = [
            "pip3 install --upgrade twine",
            "python3 -m twine upload --non-interactive --disable-progress-bar dist/*",
        ]

        return super().render()
