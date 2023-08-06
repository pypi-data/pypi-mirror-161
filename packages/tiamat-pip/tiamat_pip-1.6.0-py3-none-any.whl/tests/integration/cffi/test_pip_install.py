from tests.support.helpers import TiamatPipProject


def test_cffi(project):
    pkg_name = "cffi"

    ret = project.run("pip", "install", pkg_name)
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    assert pkg_name in ret.stdout
    installed_packages = project.get_installed_packages()
    assert pkg_name in installed_packages

    ret = project.run("pip", "uninstall", "-y", pkg_name)
    assert ret.exitcode == 0

    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert pkg_name not in ret.stdout
    installed_packages = project.get_installed_packages()
    assert pkg_name not in installed_packages


def test_cffi_upgrade(request, tmp_path):
    pkg_name = "cffi"
    pkg_version = "1.14.4"
    pkg_version_upgrade = "1.15.1"
    requirements = [
        f"{pkg_name}=={pkg_version}",
    ]
    with TiamatPipProject(
        name=pkg_name,
        path=tmp_path,
        requirements=requirements,
        one_dir=request.config.getoption("--singlebin") is False,
    ) as project:

        installed_packages = project.get_installed_packages(include_frozen=True)
        assert pkg_name in installed_packages
        assert installed_packages[pkg_name] == pkg_version

        project.copy_generated_project_to_temp()

        code = """
        import sys
        import time
        print("sys.path", sys.path)
        time.sleep(1)
        import json
        import cffi
        import _cffi_backend
        from cffi import FFI
        print(
            json.dumps(
                {
                    "cffi": cffi.__file__,
                    "_cffi_backend": _cffi_backend.__file__,
                    "sys.path": sys.path,
                }
            ),
            file=sys.stderr,
            flush=True
        )
        try:
            FFI()
        except:
            raise
        """

        ret = project.run_code(code)
        assert ret.exitcode == 0

        ret = project.run("pip", "install", "-U", f"{pkg_name}=={pkg_version_upgrade}")
        assert ret.exitcode == 0
        installed_packages = project.get_installed_packages()
        assert pkg_name in installed_packages
        assert installed_packages[pkg_name] == pkg_version_upgrade

        ret = project.run_code(code)
        assert ret.exitcode == 0
