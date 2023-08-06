"""
Tiamat pip related utilities.
"""
import logging
import os
import pprint
import sys
from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence

import distutils.command.install
import pip._internal.commands.install
import pip._internal.metadata
import pip._internal.req.req_install

from tiamatpip import configure


# Hold a reference to the real function
real_get_environment = pip._internal.metadata.get_environment

log = logging.getLogger(__name__)


def get_lib_location_guesses(
    user: bool = False,
    home: Optional[str] = None,
    root: Optional[str] = None,
    isolated: bool = False,
    prefix: Optional[str] = None,
) -> List[str]:
    """
    Patched 'pip._internal.commands.install.get_lib_location_guesses'.

    This method will return the paths proper for a tiamat-pip install.
    """
    scheme = get_tiamat_pip_scheme()
    return [scheme.purelib, scheme.platlib]


def get_tiamat_pip_scheme(*args: Any, **kwargs: Any) -> configure.TiamatPipScheme:
    """
    Override pip's get_scheme calls.

    This allows us to always return a scheme proper for tiamat-pip.
    """
    scheme = configure.TiamatPipScheme()
    log.warning(
        "Using custom TiamatPipScheme to work with tiamat-pip directory structure: %s",
        scheme,
    )
    return scheme


def patch_get_scheme() -> None:
    """
    Patch a couple of pip functions to work with tiamat-pip.
    """
    log.warning(
        "Patching 'pip._internal.commands.install.get_lib_location_guesses' to work with tiamat-pip"
    )
    pip._internal.commands.install.get_lib_location_guesses = get_lib_location_guesses
    log.warning(
        "Patching 'pip._internal.req.req_install.get_scheme' to work with tiamat-pip"
    )
    pip._internal.req.req_install.get_scheme = get_tiamat_pip_scheme  # type: ignore[attr-defined]


def patch_get_scheme_distutils() -> None:
    """
    Patch 'distutils.command.install.INSTALL_SCHEMES' to work with tiamat-pip.
    """
    scheme = configure.TiamatPipScheme()
    log.warning(
        "Patching 'distutils.command.install.INSTALL_SCHEMES' to work with tiamat-pip"
    )
    for key in distutils.command.install.INSTALL_SCHEMES:
        distutils.command.install.INSTALL_SCHEMES[key] = scheme.to_dict()
    distutils.command.install._inject_headers = (  # type: ignore[attr-defined]
        lambda name, scheme: get_tiamat_pip_scheme().to_dict()
    )


@contextmanager
def patched_environ(
    *, environ: Optional[Dict[str, str]] = None, **kwargs: str
) -> Generator[None, None, None]:
    """
    Context manager to patch ``os.environ``.
    """
    _environ = environ.copy() if environ else {}
    _environ.update(**kwargs)
    old_values = {}
    try:
        for key, value in _environ.items():
            msg_prefix = "Setting"
            if key in os.environ:
                msg_prefix = "Updating"
                old_values[key] = os.environ[key]
            log.debug(f"{msg_prefix} environ variable {key} to: '{value}'")
            os.environ[key] = value
        yield
    finally:
        for key in _environ:
            if key in old_values:
                log.debug(f"Restoring environ variable {key} to: '{old_values[key]}'")
                os.environ[key] = old_values[key]
            else:
                if key in os.environ:
                    log.debug(f"Removing environ variable {key}")
                    os.environ.pop(key)


@contextmanager
def patched_sys_argv(argv: Sequence[str]) -> Generator[None, None, None]:
    """
    Context manager to patch ``sys.argv``.
    """
    previous_sys_argv = list(sys.argv)
    try:
        log.debug(f"Patching sys.argv to: {argv}")
        sys.argv[:] = argv
        yield
    finally:
        log.debug(f"Restoring sys.argv to: {previous_sys_argv}")
        sys.argv[:] = previous_sys_argv


@contextmanager
def prepend_sys_path(
    *paths: str, excludes: Optional[List[str]] = None
) -> Generator[None, None, None]:
    """
    Context manager to prepend the passed paths to ``sys.path``.
    """
    previous_sys_path = list(sys.path)
    if excludes:
        log.debug("Exluding from sys.path: %s", excludes)
        for path in excludes:
            if path in sys.path:
                sys.path.remove(path)
    try:
        log.debug("Prepending sys.path with: %s", list(paths))
        for path in reversed(list(paths)):
            sys.path.insert(0, path)
        yield
    finally:
        log.debug(f"Restoring sys.path to: {previous_sys_path}")
        sys.path[:] = previous_sys_path


def get_default_environment():
    """
    Get the default environment where packages are installed.
    """
    log.warning(
        "Using patched ``pip._internal.metadata.get_default_environment`` to include tiamat-pip paths"
    )
    user_base_path = configure.get_user_base_path()
    assert user_base_path
    user_site_path = configure.get_user_site_path()
    assert user_site_path
    return pip._internal.metadata.get_environment(
        paths=[
            str(user_base_path),
            str(user_site_path),
        ],
    )


def get_environment(paths):
    """
    Patched ``pip._internal.metadata.get_environment`` to include tiamat-pip paths.
    """
    log.warning(
        "Using patched ``pip._internal.metadata.get_environment`` to include tiamat-pip paths"
    )
    user_base_path = configure.get_user_base_path()
    assert user_base_path
    user_site_path = configure.get_user_site_path()
    assert user_site_path
    return real_get_environment(
        paths=[
            str(user_base_path),
            str(user_site_path),
        ]
        + (paths or [])
    )


def patch_pip_internal_metadata_get_default_environment() -> None:
    """
    Patch ``pip._internal.metadata.get_default_environment``.
    """
    log.warning(
        "Patching 'pip._internal.metadata.get_default_environment' to the tiamat-pip pypath site packages"
    )
    pip._internal.metadata.get_default_environment = get_default_environment


def patch_pip_internal_metadata_get_environment() -> None:
    """
    Patch ``pip._internal.metadata.get_environment``.
    """
    log.warning(
        "Patching 'pip._internal.metadata.get_environment' to include the tiamat-pip pypath site packages"
    )
    pip._internal.metadata.get_environment = get_environment


@contextmanager
def debug_print(
    funcname: str, argv: List[str], **extra: Any
) -> Generator[None, None, None]:
    """
    Helper debug function.
    """
    prefixes_of_interest = ("TIAMAT_", "LD_", "C_", "CPATH", "CWD", "PYTHONPATH")
    environ: Dict[str, Any] = {}
    for key, value in os.environ.items():
        if key.startswith(prefixes_of_interest):
            environ[key] = value

    # Include sys.path in the debug output
    environ["sys.path"] = sys.path

    header = f"Func: {funcname}"
    tail_len = 70 - len(header) - 5
    environ_str = "\n".join(
        f"    {line}" for line in pprint.pformat(environ).splitlines()
    )
    argv_str = "\n".join(f"    {line}" for line in pprint.pformat(argv).splitlines())
    message = (
        f">>> {header} " + ">" * tail_len + "\n"
        f"  CWD: {os.getcwd()}\n"
        f"  ENVIRON:\n{environ_str}\n"
        f"  ARGV:\n{argv_str}\n"
    )
    if extra:
        message += "  EXTRA:\n"
        for key, value in extra.items():
            message += f"    {key}: {value}\n"
    log.debug(message)
    try:
        yield
    finally:
        message = f"<<< {header} " + "<" * tail_len + "\n"
        log.debug(message)
