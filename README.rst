mount
=====

|pythonver|
|license|
|ruff|

|ci|


Simple python wrapper around ``sys/mount.h``'s ``mount`` and ``umount2`` libc functions.


Installation
------------

This package is available on PyPI, so it can be installed with `pip` or
another regular package manager you use:

.. code:: sh

   python3 -m pip install mount


Usage
-----

This library is a tiny wrapper around ``mount`` and ``umount2`` functions, so
most information about them you can find in ``man 2 mount`` and ``man 2 umount``.

Generally there are only 4 objects provided by this package:

- ``mount.mount`` function that is wrapper around ``mount`` libc function.
- ``mount.umount`` function that is wrapper around ``umount2`` libc function.
- ``mount.MountFlag`` enum with available mount flags.
- ``mount.UmountFlag`` enum with available umount flags.

``mount`` and ``umount`` functions raises ``OSError`` on errors.

Here is a simple script that will mount in-memory 1G temporary filesystem
with `NOEXEC` and `NOSYMFOLLOW` flags in temporary created directory:

.. code:: python

   from tempfile import TemporaryDirectory
   from mount import mount, MountFlag


   if __name__ == "__main__":
       target = TemporaryDirectory()
       mount("tmpfs", target.name, "tmpfs", MountFlag.NOEXEC | MountFlag.NOSYMFOLLOW, "size=1G")
       print("Mounted to: ", target)


Development
-----------

The project is managed with `uv <https://docs.astral.sh/uv/>`_:

.. code:: sh

   uv sync
   uv run ruff format --check .
   uv run ruff check .
   uv run mypy
   uv run pydoclint src/mount
   uv run pytest

Tests that perform real mounts need root and are skipped without it. To run
them without touching the host mount table, start ``pytest`` in a private
mount namespace, either unprivileged through a user namespace or as real root:

.. code:: sh

   unshare -rm uv run pytest
   sudo unshare -m .venv/bin/pytest


.. |ci| image:: https://github.com/TitaniumHocker/mount/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/TitaniumHocker/mount/actions/workflows/ci.yml

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
   :target: https://github.com/astral-sh/ruff

.. |pythonver| image:: https://img.shields.io/pypi/pyversions/mount
   :alt: PyPI - Python Version

.. |license| image:: https://img.shields.io/pypi/l/mount
   :alt: PyPI - License
