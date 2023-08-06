# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2022.8.1

- Properly allow pip to uninstall older packages when upgrading them.
  Additionally:

    * Don't allow setuptools to patch distutils(makes our lives easier).
    * Define and use an install scheme compatible with tiamat-pip
    * Enforce that scheme when installing packages, including those that build C extensions
    * When installing, remove ``pypath`` from ``sys.path``, since that's
      the normal behavior of ``pip``
    * Account for pyinstaller meta importers names changing

  Fixes #18
  Fixes https://github.com/saltstack/salt/issues/62345

## [1.5.2] - 2022.7.20
- Some ``setup.py`` scripts try to import the package being installed. Fixes #16

## [1.5.1] - 2022.5.25
- Properly handle not arguments being passed to the tiamat pacakge when processing ``argv``. Fixes #14

## [1.5.0] - 2022.4.25
- Added a _fake_ command to tiamat-pip, ``frozen``. This command will list the python
dependencies which are included the tiamat binary.
- Added usage examples to the ``README.md`` file.

## [1.4.0] - 2022.4.22
- Properly parse the package name from ``pop_config`` and ``pop_config<9.0.0``. Fixes #9.
- Don't continue logic execution when running code or python files. Fixes #8

## [1.3.0] - 2021.12.17
- Upgrade supported pip to ``pip>=21.3,<21.4``
- Fix windows support. Fixes #4.

## [1.2.2] - 2021.11.08
- Restrict the supported ``pip`` versions. Uninstalling a package get's broken with ``pip>=21.0``. Fixes #7
- Drop ``globals`` usage
- Prioritize tiamat-pip ``pypath`` packages by adding a meta path entry. Fixes #5

## [1.2.1] - 2020.10.22
- Revert commit which preferred logging instead of printing errors to stderr.
These must always be visible before exiting the CLI and `--log-level=quiet` would
prevent their display.

## [1.2.0] - 2020.10.22
- Don't use pip's `setup_logging`. This actually added a `StreamHandler` writing to
`sys.stdout` breaking Salt's own logging which only writes to `sys.stderr`.
- Remove unused `tiamatpip.utils.changed_permissions` function.
- Started using `setuptools_scm` for versioning.

## [1.1.1] - 2020-10-21
- When checking installed packages from a `pkg_resources.WorkingSet()` use `.key` not
`.project_name` so that we can match against the canonicalized name.
- Print the `DistributionNotFound` exception message to `sys.stderr` and set exitcode
to 1 instead of printing the traceback.

## [1.1.0] - 2020-10-21
- Added store support to keep track of what's installed/uninstalled. Fixed #2.

## [1.0.0] - 2020-10-13
### Added
- Start keeping a changes log
- Allow showing what the library is doing by adding `TIAMAT_PIP_DEBUG=1` to the environment
- `set_user_site_packages_path` now optionaly creates the path. Set to true by default.
- tiamat-pip will now make sure the python headers are included in the generated binary so
that these are available when `pip install`'ing a package than needs to link to the "embedded"
python interpreter.

## [0.10.0] - 2020-10-09
### Added
- Make sure `pypath` comes first in sys.path

## [0.10.0rc1] - 2020-10-08
### Added
- Stopped changing permissions on the `pypath` directory.
- Error out on missing `pypath` directory

## [0.9.0] - 2020-10-01
### Added
- First working version of the project
