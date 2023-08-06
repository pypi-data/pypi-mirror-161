import logging
import os
import pathlib

import pytest

import tiamatpip
from tests.support.helpers import TiamatPipProject

log = logging.getLogger(__name__)

CODE_ROOT = pathlib.Path(tiamatpip.__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def base_requirement():
    return "pep8"


@pytest.fixture(scope="session")
def base_requirement_version():
    return "1.7.0"


@pytest.fixture(scope="session")
def built_project(request, tmpdir_factory, base_requirement, base_requirement_version):
    name = "tiamat-pip-testing"
    instance = TiamatPipProject(
        name=name,
        path=pathlib.Path(tmpdir_factory.mktemp(name, numbered=True)),
        one_dir=request.config.getoption("--singlebin") is False,
        requirements=[
            f"{base_requirement}=={base_requirement_version}",
        ],
    )
    with instance:
        if os.environ.get("CI_RUN", "0") == "0":
            instance.copy_generated_project_to_temp()
        yield instance


@pytest.fixture
def project(built_project):
    try:
        log.info("Using built Project: %s", built_project)
        yield built_project
    finally:
        built_project.delete_pypath()


# ----- CLI Options Setup ------------------------------------------------------------------------>
def pytest_addoption(parser):
    """
    Register argparse-style options and ini-style config values.
    """
    test_selection_group = parser.getgroup("Tests Selection")
    test_selection_group.addoption(
        "--singlebin",
        default=False,
        help="Choose singlebin instead of onedir to run the tests agaist.",
    )


# <---- CLI Options Setup -------------------------------------------------------------------------
