from typing import Any, Dict, List, Optional
from dataclasses import InitVar, field, dataclass

from gcip.core.job import Job
from gcip.core.rule import Rule
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.images import PredefinedImages


@dataclass(kw_only=True)
class Mirror(Job):
    """
    This job clones the CI_COMMIT_REF_NAME of the current repository and forcefully pushes this REF to the `remote_repository`.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: git-mirror
    * stage: deploy
    * image: PredefinedImages.ALPINE_GIT

    Args:
        remote_repository (str): The git repository the code of the pipelines repository should be mirrored to.
        git_config_user_email (Optional str): The 'user.email' with which the commits to the remote repository
            should be made. Defaults to GITLAB_USER_EMAIL.
        git_config_user_name (Optional str): The 'user.name' with which the commits to the remote repository
            should be made. Defaults to GITLAB_USER_NAME.
        private_key_variable (Optional str): DO NOT PROVIDE YOUR PRIVATE SSH KEY HERE!!! This parameter takes
            the name of the Gitlab environment variable, which contains the private ssh key used to push to the
            remote repository. This one should be created as protected and masked variable in the 'CI/CD' settings
            of your project.
        script_hook (Optional List(str)): This list of strings could contain any commands that should be executed
            between pulling the current repository and pushing it to the remote. This hook is mostly meant to be
            for git configuration commands, required to push to the remote repository.
        run_only_for_repository_url (Optional[str]): When mirroring to a remote Gitlab instance, you don't want to
            run this mirroring job there again. With this variable the job only runs, when its value matches
            the CI_REPOSITORY_URL of the current repository.
    """

    remote_repository: str
    git_config_user_email: str = PredefinedVariables.GITLAB_USER_EMAIL
    git_config_user_name: str = PredefinedVariables.GITLAB_USER_NAME
    private_key_variable: Optional[str] = None
    script_hook: List[str] = field(default_factory=list)
    run_only_for_repository_url: Optional[str] = None
    jobName: InitVar[str] = "git-mirror"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.ALPINE_GIT)

    def render(self) -> Dict[str, Any]:

        self._scripts = []

        if self.private_key_variable:
            self._scripts.extend(
                # this will start the ssh-agent and temporarily
                # add the ssh private key to it
                [
                    "eval $(ssh-agent -s)",
                    f"""echo "${self.private_key_variable}" | tr -d '\\r' | ssh-add - > /dev/null""",
                ]
            )

        self._scripts.extend(
            [
                "set -eo pipefail",
                "mkdir /tmp/repoReplicaUniqueDir",
                "cd /tmp/repoReplicaUniqueDir",
                f"git clone -b {PredefinedVariables.CI_COMMIT_REF_NAME} {PredefinedVariables.CI_REPOSITORY_URL} .",
                f'git config --global user.email "{self.git_config_user_email}"',
                f'git config --global user.name "{self.git_config_user_name}"',
                *self.script_hook,
                f"git push --force {self.remote_repository} {PredefinedVariables.CI_COMMIT_REF_NAME}:{PredefinedVariables.CI_COMMIT_REF_NAME}",
                f'echo "Published code to {self.remote_repository}:{PredefinedVariables.CI_COMMIT_REF_NAME}"',
            ]
        )

        if self.run_only_for_repository_url:
            self.rules.append(Rule(if_statement=f'CI_REPOSITORY_URL="{self.run_only_for_repository_url}"'))

        return super().render()
