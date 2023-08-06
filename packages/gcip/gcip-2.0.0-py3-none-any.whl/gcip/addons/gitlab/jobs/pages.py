import os
from typing import Any, Dict
from dataclasses import InitVar, dataclass

from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables
from gcip.addons.python.scripts import (
    pip_install_requirements,
)


def _gitlab_pages_path(subpath: str) -> str:
    """
    Ensures `subpath` is a subpath under `./public`.

    Args:
        subpath (str): Any path string is allowed, with or without leading slash.

    Returns:
        str: The path string `public/<subpath>`
    """
    if subpath != "":
        subpath = os.path.normpath(subpath)

        if os.path.isabs(subpath):
            subpath = subpath[1:]

    return os.path.join("public", subpath)


@dataclass(kw_only=True)
class AsciiDoctor(Job):
    """
    Translate the AsciiDoc source FILE as Gitlab Pages HTML5 file.

    Runs `asciidoctor {source} -o public{out_file}`and stores the output
    as artifact under the `public` directory.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: asciidoctor-pages
    * stage: build
    * image: ruby:3-alpine
    * artifacts: Path 'public'

    Args:
        source (str): Source .adoc files to translate to HTML files.
        out_file (str): Output HTML file.
    """

    source: str
    out_file: str
    jobName: InitVar[str] = "asciidoctor-pages"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image("ruby:3-alpine")
        self.artifacts.add_paths("public")

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            "gem install asciidoctor",
            f"asciidoctor {self.source} -o {_gitlab_pages_path(self.out_file)}",
        ]
        return super().render()


@dataclass(kw_only=True)
class Sphinx(Job):
    """
    Runs `sphinx-build -b html -E -a docs public/${CI_COMMIT_REF_NAME}` and installs project requirements
    before (`pip_install_requirements()`)

    * Requires a `docs/requirements.txt` in your project folder` containing at least `sphinx`
    * Creates it artifacts for Gitlab Pages under `pages`

    This subclass of `Job` will configure following defaults for the superclass:

    * name: sphinx-pages
    * stage: build
    * artifacts: Path 'public'
    """

    jobName: InitVar[str] = "sphinx-pages"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.artifacts.add_paths("public")

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            pip_install_requirements("docs/requirements.txt"),
            f"sphinx-build -b html -E -a docs {_gitlab_pages_path(PredefinedVariables.CI_COMMIT_REF_SLUG)}",
        ]
        return super().render()


@dataclass(kw_only=True)
class Pdoc3(Job):
    """Generate a HTML API documentation of you python code as Gitlab Pages.

    Runs `pdoc3 --html -f --skip-errors --output-dir public{path} {module}` and stores the output
    as artifact under the `public` directory.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: pdoc3-pages
    * stage: build
    * artifacts: Path 'public'

    Args:
        module (str): The Python module name. This may be an import path resolvable in the current environment,
            or a file path to a Python module or package.
        output_path (str, optional): A sub path of the Gitlab Pages `public` directory to output generated HTML/markdown files to. Defaults to "/".

    Returns:
        Job: The Gitlab CI job generating Gitlab Pages with pdoc3.
    """

    module: str
    output_path: str = ""
    jobName: InitVar[str] = "pdoc3-pages"
    jobStage: InitVar[str] = "build"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.artifacts.add_paths("public")

    def render(self) -> Dict[str, Any]:
        self._scripts = [
            "pip3 install pdoc3",
            f"pdoc3 --html -f --skip-errors --output-dir {_gitlab_pages_path(self.output_path)} {self.module}",
        ]
        return super().render()
