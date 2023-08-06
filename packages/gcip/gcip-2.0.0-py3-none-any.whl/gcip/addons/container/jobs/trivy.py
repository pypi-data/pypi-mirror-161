from os import path
from typing import Any, Dict, Optional
from dataclasses import InitVar, dataclass

from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.images import PredefinedImages


@dataclass(kw_only=True)
class ScanLocalImage(Job):
    """This job scanns container images to find vulnerabilities.

    This job fails with exit code 1 if severities are found.
    The scan output is printed to stdout and uploaded to the artifacts of GitLab.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: trivy
    * stage: check
    * image: PredefinedImages.TRIVY
    * artifacts: Path 'trivy.txt'

    Args:
        image_path (Optional[str]): Path where to find the container image.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
        image_name (Optional[str]): Container image name, searched for in `image_path` and gets `.tar` appended.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
        output_format (Optional[str]): Scan output format, possible values (table, json). Internal default `table`.
            Defaults to None.
        severity (Optional[str]): Severities of vulnerabilities to be displayed (comma separated).
            Defaults internally to "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL". Defaults to None.
        vulnerability_types (Optional[str]): List of vulnerability types (comma separated).
            Defaults internally to "os,library". Defaults to None.
        exit_if_vulnerable (bool): Exit code when vulnerabilities were found. If true exit code is 1 else 0. Defaults to True.
        trivy_config (Optional[str]): Additional options to pass to `trivy` binary. Defaults to None.

        Raises:
        ScriptArgumentNotAllowedError: It is not allowed to use the `script` argument in **kwargs,
            `script` is already initialized.
    """

    image_path: str = PredefinedVariables.CI_PROJECT_DIR
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    output_format: Optional[str] = None
    severity: Optional[str] = None
    vulnerability_types: Optional[str] = None
    exit_if_vulnerable: bool = True
    trivy_config: Optional[str] = None
    jobName: InitVar[str] = "trivy"
    jobStage: InitVar[str] = "check"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        self.image_name = self.image_name.replace("/", "_")

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.TRIVY)
        self.artifacts.add_paths("trivi.txt")

    def render(self) -> Dict[str, Any]:
        trivy_cmd = ["trivy image"]
        trivy_cmd.append(f"--input {self.image_path}/{self.image_name}.tar")
        trivy_cmd.append("--no-progress")

        if self.output_format:
            trivy_cmd.append(f"--format {self.output_format}")

        if self.severity:
            trivy_cmd.append(f"--severity {self.severity}")

        if self.vulnerability_types:
            trivy_cmd.append(f"--vuln-type {self.vulnerability_types}")

        if self.exit_if_vulnerable:
            trivy_cmd.append("--exit-code 1")

        if self.trivy_config:
            trivy_cmd.append(self.trivy_config)

        trivy_cmd.append("|tee " + path.join(PredefinedVariables.CI_PROJECT_DIR, "trivi.txt"))

        self._scripts = [
            "set -eo pipefail",
            " ".join(trivy_cmd),
            "trivy --version",
        ]
        return super().render()


@dataclass(kw_only=True)
class TrivyIgnoreFileCheck(Job):
    """
    This job checks if a .trivyignore file exists and is not empty and fails if so.

    If a .trivyignore file is found and not empty, by default the job fails with `exit 1`,
    the job is configured to allow failures so that the pipeline keeps running.
    This ensures the visibility of acknowledged CVE's in the .trivyignore file inside the pipline.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: trivyignore
    * stage: check
    * image: PredefinedImages.BUSYBOX
    * allow_failure: 1

    Args:
        trivyignore_path (Optional[str], optional): Path to the `.trivyignore` file. Defaults to `$CI_PROJECT_DIR/.trivyignore`.

    Raises:
        ScriptArgumentNotAllowedError: It is not allowed to use the `script` argument in **kwargs,
            `script` is already initialized.
    """

    trivyignore_path: str = f"{PredefinedVariables.CI_PROJECT_DIR}/.trivyignore"
    jobName: InitVar[str] = "trivyignore"
    jobStage: InitVar[str] = "check"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.BUSYBOX)
        self.set_allow_failure(1)

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            "set -eo pipefail",
            f'test -f {self.trivyignore_path} || {{ echo "{self.trivyignore_path} does not exists."; exit 0; }}',
            # The grep-regex (-E) will check for everything but (-v) empty lines ('^ *$') and comments (first character is '#')
            f"grep -vE '^ *(#.*)?$' {self.trivyignore_path} || {{ echo '{self.trivyignore_path} found but empty.'; exit 0; }}",
            f'echo "{self.trivyignore_path} not empty. Please check your vulnerabilities!"; exit 1;',
        ]
        return super().render()
