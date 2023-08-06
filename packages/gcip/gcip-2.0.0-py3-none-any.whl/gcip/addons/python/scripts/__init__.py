__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


def pip_install_requirements(requirements_file: str = "requirements.txt") -> str:
    """
    Installs Python requirements from Pipfile.lock and requirements.txt.

    This function returns a bash command which does the following:

    * It checks if there is a Pipfile.lock
    * If so, it install pipenv and then installs requirements directly into the system with `pipenv install --system`.
    * The script then checks if there is a requirements file (`requirements.txt` by default).
    * If so, it installs it by running `pip install --upgrade -r <requirements_file>`.

    :arg requirements_file: Defaults to `requirements.txt`
    """
    return (
        "if test -f Pipfile.lock; then pip install pipenv; pipenv install --dev --system; fi; "
        f"if test -f {requirements_file}; then pip install --upgrade -r {requirements_file}; fi"
    )
