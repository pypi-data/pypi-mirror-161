"""
Test single python module packages installations.
"""
import pytest


@pytest.fixture(params=["future"])
def package(request):
    return request.param


def test_setup_py_imports_package(project, package):
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert package not in ret.stdout

    ret = project.run("pip", "install", package)
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert package in ret.stdout

    ret = project.run("pip", "uninstall", "-y", package)
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert package not in ret.stdout


def test_docopt(project):
    package = "docopt"
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert package not in ret.stdout

    ret = project.run("pip", "install", f"{package}==0.5.0")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert package in ret.stdout
    installed_packages = project.get_installed_packages()
    assert package in installed_packages
    assert installed_packages[package] == "0.5.0"

    ret = project.run("pip", "install", f"{package}==0.6.0")
    assert ret.exitcode == 0
    assert package in ret.stdout
    installed_packages = project.get_installed_packages()
    assert package in installed_packages
    assert installed_packages[package] == "0.6.0"

    ret = project.run("pip", "uninstall", "-y", package)
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert package not in ret.stdout
    installed_packages = project.get_installed_packages()
    assert package not in installed_packages


def test_docker_compose_with_older_docopt(project):
    dep = "docopt"
    dep_initial_version = "0.5.0"
    package = "docker-compose"
    package_version = "1.29.2"
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert dep not in ret.stdout
    assert package not in ret.stdout

    ret = project.run("pip", "install", f"{dep}=={dep_initial_version}")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert dep in ret.stdout
    installed_packages = project.get_installed_packages()
    assert dep in installed_packages
    assert installed_packages[dep] == dep_initial_version

    ret = project.run("pip", "install", f"{package}=={package_version}")
    assert ret.exitcode == 0
    assert package in ret.stdout
    installed_packages = project.get_installed_packages()
    assert package in installed_packages
    assert installed_packages[package] == package_version
    assert dep in installed_packages
    assert installed_packages[dep] != dep_initial_version
