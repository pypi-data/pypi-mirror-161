def install_packages(*packages: str, with_sudo: bool = False) -> str:
    """
    This function returns a shell command which checks which Linux package manger is available
    and installs a package. This is useful if you want to install a package within a Gitlab
    job but did not know on which system the job will be running on.

    Currently supported are apk, apt-get, yum, dnf and zypper.

    The drawback of this function is, that it only supports one package name. So if different
    package managers have different names for a package, this script will fail.

    Source: https://unix.stackexchange.com/a/571192/139685

    Args:
        packages (str): A string which lists all the packages that should be installed, separated
                        by whitespaces.
        with_sudo (bool): If the command(s) should be executed with sudo. Defaults to False.
    """
    sudo = "sudo" if with_sudo else ""
    package_list = " ".join(packages)
    return (
        f"""if [ -x "$(command -v apk)" ]; then {sudo} apk update && {sudo} apk add --yes --no-cache {package_list}; """
        f"""elif [ -x "$(command -v apt-get)" ]; then {sudo} apt-get update && {sudo} apt-get install --yes {package_list}; """
        f"""elif [ -x "$(command -v yum)" ]; then {sudo} yum install -y {package_list}; """
        f"""elif [ -x "$(command -v dnf)" ]; then {sudo} dnf install -y {package_list}; """
        f"""elif [ -x "$(command -v zypper)" ]; then {sudo} zypper install -y {package_list}; """
        f"""else echo "FAILED TO INSTALL PACKAGE: Package manager not found. You must manually install: {package_list}">&2; fi"""
    )
