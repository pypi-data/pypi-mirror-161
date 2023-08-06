"""This modules provide Jobs executing [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/) scripts

Those require [Docker to be installed](https://docs.docker.com/engine/install/) on the Gitlab runner.
"""

from typing import Any, Dict, Optional
from dataclasses import InitVar, dataclass

from gcip.core.job import Job

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


@dataclass(kw_only=True)
class Build(Job):
    """Runs [```docker build```](https://docs.docker.com/engine/reference/commandline/build/)

    Example:

    ```
    from gcip.addons.container.job.docker import Build
    build_job = Build(BuildOpts(repository="myrepo/myimage", tag="v0.1.0"))
    ```

    This subclass of `Job` will configure following defaults for the superclass:

    * name: docker
    * stage: build

    Args:
        repository (str): The Docker repository name ```([<registry>/]<image>)```.
        tag (Optional[str]): A Docker image tag applied to the image. Defaults to `None` which no tag is provided
            to the docker build command. Docker should then apply the default tag ```latest```.
        context (str): The Docker build context (the directory containing the Dockerfile). Defaults to
            the current directory `.`.
    """

    repository: str
    tag: Optional[str] = None
    context: str = "."
    jobName: InitVar[str] = "docker"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.add_variables(DOCKER_DRIVER="overlay2", DOCKER_TLS_CERTDIR="")

    def render(self) -> Dict[str, Any]:
        fq_image_name = self.repository
        if self.tag:
            fq_image_name += f":{self.tag}"

        self._scripts = [f"docker build -t {fq_image_name} {self.context}"]
        return super().render()


@dataclass(kw_only=True)
class Push(Job):
    """Runs [```docker push```](https://docs.docker.com/engine/reference/commandline/push/)
    and optionally [```docker login```](https://docs.docker.com/engine/reference/commandline/login/) before.

    Example:

    ```python
    from gcip.addons.container.docker import Push
    push_job = Push(PushOpts(
                    registry="docker.pkg.github.com/dbsystel/gitlab-ci-python-library",
                    image="gcip",
                    tag="v0.1.0",
                    user_env_var="DOCKER_USER",
                    login_env_var="DOCKER_TOKEN"
                ))
    ```

    The `user_env_var` and `login_env_var` should be created as *protected* and *masked*
    [custom environment variable configured
    in the UI](https://git.tech.rz.db.de/help/ci/variables/README#create-a-custom-variable-in-the-ui).

    This subclass of `Job` will configure following defaults for the superclass:

    * name: docker
    * stage: deploy

    Args:
        registry (Optional[str]): The Docker registry the image should be pushed to.
            Defaults to `None` which targets to the official Docker Registry at hub.docker.com.
        image (str): The name of the Docker image to push to the `registry`.
        tag (Optional[str]): The Docker image tag that should be pushed to the `registry`. Defaults to ```latest```.
        user_env_var (Optional[str]): If you have to login to the registry before the push, you have to provide
            the name of the environment variable, which contains the username value, here.
            **DO NOT PROVIDE THE USERNAME VALUE ITSELF!** This would be a security issue!
            Defaults to `None` which skips the docker login attempt.
        login_env_var (Optional[str]): If you have to login to the registry before the push, you have to provide
            the name of the environment variable, which contains the password or token, here.
            **DO NOT PROVIDE THE LOGIN VALUE ITSELF!** This would be a security issue!
            Defaults to `None` which skips the docker login attempt.
    """

    container_image: str
    registry: Optional[str] = None
    tag: Optional[str] = None
    user_env_var: Optional[str] = None
    login_env_var: Optional[str] = None
    jobName: InitVar[str] = "docker"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)

    def render(self) -> Dict[str, Any]:
        self._scripts = []
        if self.user_env_var and self.login_env_var:
            self._scripts.append(f'docker login -u "${self.user_env_var}" -p "${self.login_env_var}"')

        fq_image_name = self.container_image
        if self.registry:
            fq_image_name = f"{self.registry}/{fq_image_name}"
        if self.tag:
            fq_image_name += f":{self.tag}"

        self._scripts.append(f"docker push {fq_image_name}")
        return super().render()
