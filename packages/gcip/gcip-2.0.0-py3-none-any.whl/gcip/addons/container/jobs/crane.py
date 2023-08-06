import os
from typing import Any, Dict, Union, Optional
from dataclasses import InitVar, field, dataclass

from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.config import DockerClientConfig
from gcip.addons.container.images import PredefinedImages
from gcip.addons.container.registries import Registry


@dataclass(kw_only=True)
class Copy(Job):
    """
    Creates a job to copy container images with `crane`.
    See [`crane`](https://github.com/google/go-containerregistry/tree/main/cmd/crane)

    Copying an image is usfull, if you want to have container images as close as possible
    to your cluster or servers.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane-copy
    * stage: deploy
    * image: PredefinedImages.CRANE

    Args:
        src_registry (str): Registry URL to copy container image from.
        dst_registry (str): Registry URL to copy container image to.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            used by crane to authenticate against given registries. Defaults to None.
    """

    src_registry: Union[Registry, str]
    dst_registry: Union[Registry, str]
    docker_client_config: Optional[DockerClientConfig] = None
    jobName: InitVar[str] = "crane-copy"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> Dict[str, Any]:
        if self.docker_client_config:
            self._scripts = self.docker_client_config.get_shell_command()
        else:
            self._scripts = []

        self._scripts.extend(
            [
                f"crane validate --remote {self.src_registry}",
                f"crane copy {self.src_registry} {self.dst_registry}",
            ]
        )

        return super().render()


@dataclass(kw_only=True)
class Push(Job):
    """
    Creates a job to push container image to remote container registry with `crane`.

    The image to copy must be in a `tarball` format. It gets validated with crane
    and is pushed to `dst_registry` destination registry.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane-push
    * stage: deploy
    * image: PredefinedImages.CRANE

    Args:
        dst_registry (str): Registry URL to copy container image to.
        tar_path (Optional[str], optional): Path where to find the container image tarball.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
        image_name (Optional[str], optional): Container image name, searched for in `image_path` and gets `.tar` appended.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
        image_tag (Optional[str]): The tag the image will be tagged with.
            Defaults to `PredefinedVariables.CI_COMMIT_REF_NAME` or `PredefinedVariables.CI_COMMIT_TAG`.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
            and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
    """

    dst_registry: Union[Registry, str]
    tar_path: str = PredefinedVariables.CI_PROJECT_DIR
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: Optional[str] = None
    docker_client_config: DockerClientConfig = field(default_factory=lambda: DockerClientConfig().add_auth(registry=Registry.DOCKER))
    jobName: InitVar[str] = "crane-push"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        if not self.image_tag:
            if PredefinedVariables.CI_COMMIT_TAG:
                self.image_tag = PredefinedVariables.CI_COMMIT_TAG
            else:
                self.image_tag = PredefinedVariables.CI_COMMIT_REF_NAME

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> Dict[str, Any]:

        image_path = self.image_name.replace("/", "_")

        self._scripts = self.docker_client_config.get_shell_command()
        self._scripts.extend(
            [
                f"crane validate --tarball {self.tar_path}/{image_path}.tar",
                f"crane push {self.tar_path}/{image_path}.tar {self.dst_registry}/{self.image_name}:{self.image_tag}",
            ]
        )

        if self.image_tag in ["main", "master"]:
            self._scripts.append(f"crane push {self.tar_path}/{image_path}.tar {self.dst_registry}/{self.image_name}:latest")

        return super().render()


@dataclass(kw_only=True)
class Pull(Job):
    """
    Creates a job to pull container image from remote container registry with `crane`.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane
    * stage: pull
    * image: PredefinedImages.CRANE

    Args:
        src_registry (str): Registry URL to pull container image from.
        image_name (str): Container image with namespace to pull from `src_registry`.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
        image_tag (str): Tag of the image which will be pulled. Defaults to "latest".
        tar_path (Optional[str], optional): Path where to save the container image tarball.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
            and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
    """

    src_registry: Union[Registry, str]
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: str = "latest"
    tar_path: str = PredefinedVariables.CI_PROJECT_DIR
    docker_client_config: DockerClientConfig = field(default_factory=lambda: DockerClientConfig().add_auth(registry=Registry.DOCKER))
    jobName: InitVar[str] = "crane"
    jobStage: InitVar[str] = "pull"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> Dict[str, Any]:
        image_path = self.image_name.replace("/", "_")

        self._scripts = self.docker_client_config.get_shell_command()

        self._scripts.extend(
            [
                f"mkdir -p {os.path.normpath(self.tar_path)}",
                f"crane pull {self.src_registry}/{self.image_name}:{self.image_tag} {self.tar_path}/{image_path}.tar",
            ]
        )
        return super().render()
