"""
Test the pip install of docker-compose.
"""


def test_docker_compose(project):
    pkg_name = "docker-compose"
    pkg_version = "1.29.2"
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert pkg_name not in ret.stdout

    ret = project.run("pip", "install", f"{pkg_name}=={pkg_version}")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert pkg_name in ret.stdout

    ret = project.run("pip", "uninstall", "-y", pkg_name)
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert pkg_name not in ret.stdout
