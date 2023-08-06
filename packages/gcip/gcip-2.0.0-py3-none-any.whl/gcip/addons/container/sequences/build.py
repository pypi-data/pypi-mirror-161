__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Daniel von Eßen"
__email__ = "daniel.von-essen@deutschebahn.com"

from typing import Union, Optional
from dataclasses import dataclass

from gcip.core.cache import Cache
from gcip.core.sequence import Sequence
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.jobs import (
    dive,
    crane,
    trivy,
    kaniko,
)
from gcip.addons.container.registries import Registry


@dataclass(kw_only=True)
class FullContainerSequenceOpts:
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: Optional[str] = None
    registry: Union[Registry, str] = Registry.DOCKER
    do_dive_scan: bool = True
    do_trivy_scan: bool = True
    do_trivy_ignore_file_check: bool = True
    do_crane_push: bool = True


class FullContainerSequence(Sequence):
    def __init__(
        self,
        *,
        image_name: str = PredefinedVariables.CI_PROJECT_NAME,
        image_tag: Optional[str] = None,
        registry: Union[Registry, str] = Registry.DOCKER,
        do_dive_scan: bool = True,
        do_trivy_scan: bool = True,
        do_trivy_ignore_file_check: bool = True,
        do_crane_push: bool = True,
    ) -> None:
        """
        Creates a `gcip.Sequence` to build, scan and push a container image.

        The build step is executed by `gcip.addons.container.jobs.kaniko.execute`, it will build the container image an outputs it to a tarball.
        There are two scan's, optimization scan with `gcip.addons.container.jobs.dive.scan_local_image` to scan storage wasting in container image
        and a vulnerability scan with `gcip.addons.container.jobs.trivy.scan`. Both outputs are uploaded as an artifact to the GitLab instance.
        The container image is uploaded with `gcip.addons.container.jobs.crane.push`.

        Args:
            registry (Union[Registry, str], optional): Container registry to push the image to. If the container registry needs authentication,
                you have to provide a `gcip.addons.container.config.DockerClientConfig` object with credentials. Defaults to Registry.DOCKER.
            image_name (Optional[str]): Image name with stage in the registry. e.g. username/image_name.
                Defaults to `gcip.core.variables.PredefinedVariables.CI_PROJECT_NAME`.
            image_tag (Optional[str]): Image tag. The default is either `PredefinedVariables.CI_COMMIT_TAG` or
                `PredefinedVariables.CI_COMMIT_REF_NAME` depending of building from a git tag or from a branch.
            docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
                to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
                and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
            do_dive_scan (Optional[bool]): Set to `False` to skip the Dive scan job. Defaults to True.
            do_trivy_scan (Optional[bool]): Set to `False` to skip the Trivy scan job. Defaults to True.
            do_trivyignore_check (Optional[bool]): Set to `False` to skip the existance check of the `.trivyignore` file. Defaults to True.
            do_crane_push (Optional[bool]): Set to `False` to skip the Crane push job. Defaults to True.
        """
        super().__init__()

        self.cache = Cache(paths=["image"])

        #
        # kaniko
        #
        self.kaniko_execute_job = kaniko.Execute(image_name=image_name, image_tag=image_tag, registries=[registry], tar_path=self.cache.paths[0])
        self.kaniko_execute_job.set_cache(self.cache)
        self.add_children(self.kaniko_execute_job)

        #
        # dive
        #
        self.dive_scan_job = dive.Scan(image_name=image_name, image_path=self.cache.paths[0])
        self.dive_scan_job.set_cache(self.cache)
        if do_dive_scan:
            self.add_children(self.dive_scan_job)

        #
        # trivy
        #
        self.trivy_scan_job = trivy.ScanLocalImage(image_name=image_name, image_path=self.cache.paths[0])
        self.trivy_scan_job.set_cache(self.cache)
        if do_trivy_scan:
            self.add_children(self.trivy_scan_job)

        #
        # trivy ignore file check
        #
        self.trivy_ignore_file_check_job = trivy.TrivyIgnoreFileCheck()
        if do_trivy_ignore_file_check:
            self.add_children(self.trivy_ignore_file_check_job)

        #
        # crane push
        #
        self.crane_push_job = crane.Push(dst_registry=registry, image_name=image_name, image_tag=image_tag, tar_path=self.cache.paths[0])
        self.crane_push_job.set_cache(self.cache)
        if do_crane_push:
            self.add_children(self.crane_push_job)
