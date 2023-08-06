import os
from typing import Any, Dict, List, Union, Optional
from dataclasses import InitVar, field, dataclass

from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.config import DockerClientConfig
from gcip.addons.container.images import PredefinedImages
from gcip.addons.container.registries import Registry

__author__ = "Daniel von Eßen"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Daniel von Eßen", "Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


@dataclass(kw_only=True)
class Execute(Job):
    """
    Creates a job which builds container images.

    This job creates images depending on git branches.
    e.g If the branch which gets pushed to the remote is named `my_awsome_feature` the image will be tagged with `my-awsome-feature`.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: kaniko
    * stage: build
    * image: PredefinedImages.KANIKO

    Args:
        context (Optional[str], optional): Context which will be send to kaniko. Defaults to `None` which implies the local
            directory is the context.
        image_name (Optional[str], optional): Image name which will be created. Defaults to PredefinedVariables.CI_PROJECT_NAME.
        image_tag (Optional[str]): The tag the image will be tagged with.
            Defaults to `PredefinedVariables.CI_COMMIT_REF_NAME` or `PredefinedVariables.CI_COMMIT_TAG`.
        registries (Optional[List[str]], optional): List of container registries to push created image to. Defaults to an empty list.
        tar_path (Optional[str], optional): Container images created by kaniko are tarball files.
            This is the path where to store the image, will be named with suffix `.tar`. This path will be created if not present.
            Defaults to `None` which implies the image will be pushed to ```hub.docker.com```.
        build_args (Dict[str, str], optional): Container build arguments, used to instrument the container image build. Defaults to {}.
        build_target (Optional[str], optional): For container multistage builds name of the build stage you want to create.
            Image tag will be appended with the build_target. e.g. latest-buildtarget. Defaults to None.
        dockerfile (str, optional): Name of the dockerfile to use. File is relative to context. Defaults to "Dockerfile".
        enable_push (bool, optional): Enable push to container registry, disabled to allow subsequent jobs to act on container tarball.
            Defaults to False.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
            and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
        verbosity (str, optional): Verbosity of kaniko logging. Defaults to "info".
    """

    context: str = PredefinedVariables.CI_PROJECT_DIR
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: Optional[str] = None
    registries: Optional[List[Union[Registry, str]]] = None
    tar_path: Optional[str] = None
    build_args: Optional[Dict[str, str]] = None
    build_target: Optional[str] = None
    dockerfile: str = f"{PredefinedVariables.CI_PROJECT_DIR}/Dockerfile"
    enable_push: bool = False
    docker_client_config: DockerClientConfig = field(default_factory=lambda: DockerClientConfig().add_auth(registry=Registry.DOCKER))
    verbosity: Optional[str] = None
    jobName: InitVar[str] = "kaniko"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:

        if not self.image_tag:
            if PredefinedVariables.CI_COMMIT_TAG:
                self.image_tag = PredefinedVariables.CI_COMMIT_TAG
            elif PredefinedVariables.CI_COMMIT_REF_NAME:
                self.image_tag = PredefinedVariables.CI_COMMIT_REF_NAME

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.KANIKO)

    def render(self) -> Dict[str, Any]:

        # Set static config path. Kaniko uses /kaniko/.docker/config.json path
        self.docker_client_config.set_config_file_path("/kaniko/.docker/config.json")
        self._scripts = self.docker_client_config.get_shell_command()

        self.context = os.path.normpath(self.context)

        executor_cmd = ["executor"]
        executor_cmd.append(f"--context {self.context}")
        executor_cmd.append(f"--dockerfile {self.dockerfile}")

        if self.tar_path:
            self._scripts.append(f"mkdir -p {os.path.normpath(self.tar_path)}")
            image_path = self.image_name.replace("/", "_")
            executor_cmd.append(f"--tarPath {os.path.join(self.tar_path, image_path)}.tar")

        if self.verbosity:
            executor_cmd.append(f"--verbosity {self.verbosity}")

        # Disable push to registries.
        if not self.enable_push:
            executor_cmd.append("--no-push")

        # Check if multistage build is wanted.
        # Add --target flag to executor and prefix build_target "-"
        build_target_postfix = ""
        if self.build_target:
            executor_cmd.append(f"--target {self.build_target}")
            build_target_postfix = f"-{self.build_target}"

        # Compose build arguments.
        if self.build_args:
            for k, v in self.build_args.items():
                executor_cmd.append(f"--build-arg '{k}={v}'")

        image_tag_postfix = ""
        if self.image_tag:
            image_tag_postfix = f":{self.image_tag}"

        # Extend executor command with --destination per registry
        if self.registries is None or len(self.registries) == 0:
            executor_cmd.append(f"--destination {self.image_name}{image_tag_postfix}{build_target_postfix}")
            if self.image_tag and self.image_tag in ["main", "master"]:
                executor_cmd.append(f"--destination {self.image_name}:latest{build_target_postfix}")

        if self.registries:
            for registry in self.registries:
                executor_cmd.append(f"--destination {registry}/{self.image_name}{image_tag_postfix}{build_target_postfix}")
                if self.image_tag and self.image_tag in ["main", "master"]:
                    executor_cmd.append(f"--destination {registry}/{self.image_name}:latest{build_target_postfix}")

        self._scripts.append(" ".join(executor_cmd))

        return super().render()
