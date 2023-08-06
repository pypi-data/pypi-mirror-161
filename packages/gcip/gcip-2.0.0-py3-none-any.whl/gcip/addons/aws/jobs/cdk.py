import warnings
from typing import Any, Dict, List, Optional
from dataclasses import InitVar, field, dataclass

from gcip.core.job import Job


@dataclass(kw_only=True)
class Bootstrap(Job):
    aws_account_id: str
    aws_region: str
    toolkit_stack_name: str
    qualifier: str
    resource_tags: Optional[Dict[str, str]] = None
    jobName: InitVar[str] = "toolkit-stack"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        """
        This job has a lot of custom configuration options. With the `job_opts` parameter, you can control the basic `Job` configuration.
        However this is not necessary. The Execute jobs has following defaults for the basic `Job` configuration:

            * `job_opts.name` defaults to `toolkit-stack`
            * `job_opts.stage` defaults to `deploy`
              contain the `crane` binary.
        """

        super().__init__(script="", name=jobName, stage=jobStage)
        self.add_variables(CDK_NEW_BOOTSTRAP="1")

    def render(self) -> Dict[str, Any]:
        script = [
            "cdk bootstrap",
            f"--toolkit-stack-name {self.toolkit_stack_name}",
            f"--qualifier {self.qualifier}",
            f"aws://{self.aws_account_id}/{self.aws_region}",
        ]

        if self.resource_tags:
            script.extend([f"-t {k}={v}" for k, v in self.resource_tags.items()])

        self._scripts = [" ".join(script)]
        return super().render()


@dataclass(kw_only=True)
class Deploy(Job):
    stacks: List[str] = field(default_factory=list)
    toolkit_stack_name: Optional[str] = None
    strict: bool = True
    wait_for_stack: bool = True
    wait_for_stack_assume_role: Optional[str] = None
    wait_for_stack_account_id: Optional[str] = None
    deploy_options: Optional[str] = None
    context: Optional[Dict[str, str]] = None
    jobName: InitVar[str] = "cdk"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        self._scripts = []

        stacks_string = " ".join(self.stacks)
        script = ["cdk deploy --require-approval 'never'"]

        if self.strict:
            script.append("--strict")

        if self.deploy_options:
            script.append(self.deploy_options)

        if self.context:
            script.extend([f"-c {k}={v}" for k, v in self.context.items()])

        script.append(f"--toolkit-stack-name {self.toolkit_stack_name}")
        script.append(stacks_string)

        if self.wait_for_stack:
            wait_for_stack_options = ""
            if self.wait_for_stack_assume_role:
                wait_for_stack_options += f" --assume-role {self.wait_for_stack_assume_role}"
                if self.wait_for_stack_account_id:
                    wait_for_stack_options += f" --assume-role-account-id {self.wait_for_stack_account_id}"
            elif self.wait_for_stack_account_id:
                warnings.warn("`wait_for_stack_account_id` has no effects without `wait_for_stack_assume_role`")

            self._scripts.extend(
                [
                    "pip3 install gcip",
                    f"python3 -m gcip.addons.aws.tools.wait_for_cloudformation_stack_ready --stack-names '{stacks_string}'{wait_for_stack_options}",
                ]
            )

        self._scripts.append(" ".join(script))
        return super().render()


@dataclass(kw_only=True)
class Diff(Job):
    stacks: List[str] = field(default_factory=list)
    diff_options: Optional[str] = None
    context: Optional[Dict[str, str]] = None
    jobName: InitVar[str] = "cdk"
    jobStage: InitVar[str] = "diff"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        script = ["cdk diff"]
        if self.diff_options:
            script.append(self.diff_options)

        if self.context:
            script.extend([f"-c {k}={v}" for k, v in self.context.items()])

        script.append(" ".join(self.stacks))

        self._scripts = [" ".join(script)]
        return super().render()
