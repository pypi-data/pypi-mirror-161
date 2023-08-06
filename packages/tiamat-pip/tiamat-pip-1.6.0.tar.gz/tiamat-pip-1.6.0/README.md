# Tiamat Pip

Pip handling for tiamat projects

## Setup
In order to be able to `pip install` packages which can be used with your tiamat packaged application
you need to add `tiamat-pip` as a dependency and your `run.py` should look similar to:

```python
#!/usr/bin/env python3

import sys
import multiprocessing

import tiamatpip.cli
import tiamatpip.configure

import mainapp

# Configure the path where to install the new packages
tiamatpip.configure.set_user_site_packages_path("THIS SHOULD BE A HARDCODED PATH")


def main(argv):
    # Let's see if we should be handling pip related stuff
    if tiamatpip.cli.should_redirect_argv(argv):
        tiamatpip.cli.process_pip_argv(argv)
        # You can choose to `return` but there's really no need since the pip command
        # interceptions will trigger a `sys.exit` with the appropriate exit code.

    # If we reached this far, it means we're not handling pip stuff
    # Your application logic can resume

    mainapp.main(argv)
    sys.exit(0)


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        multiprocessing.freeze_support()
    main(sys.argv)
```

## Usage

When your package is compiled with tiamat and includes tiamat-pip, the ``pip`` commands get
intercepted and the code logic runs within your packaged binary python runtime.

All ``pip`` commands and their respective CLI flags are supported.

### Showing the ``pip`` usage and help

```shell
your-project-binary pip --help
```

```shell
your-project-binary pip install --help
```

### Installing a python package

```shell
your-project-binary pip install foo
```

```shell
your-project-binary pip install foo>=2.1.0
```

### Listing installed packages

```shell
your-project-binary pip list
```

This will list all of the python packages that were installed using pip, which,
**are not included in the binary**.

### Listing packages shipped with the binary

If you want to know which packages, and their respective versions, were shipped
with the tiamat binary, issue the following command:

```shell
your-project-binary pip frozen
```

This command **is not supported by ``pip``**. We intercept the call and get the
package listing from the right place.
The CLI flags for this command are the same as for ``pip list``.

### Uninstalling a package

```shell
your-project-binary pip uninstall foo
```

**ATTENTION**: Only the packages installed by pip can be uninstalled. The packages
that were shipped with the binary **cannot** be uninstalled.

## Known Issues

* Getting the version of an upgraded package using ``pkg_resources.get_distribution(pkgname).version``
returns the version of the package that was shipped with the tiamat binary and not the upgraded package
version. See [#11](https://gitlab.com/saltstack/pop/tiamat-pip/-/issues/11) for more information.
