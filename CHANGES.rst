#########
Changelog
#########

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0>`_.

.. contents:: Contents

2.0.0
=====

Unreleased.

Removed
-------

- ``pymnt`` command and ``python -m mount`` entrypoint. Use ``mount(8)`` and
  ``umount(8)`` from the command line, this package only provides
  programmatic access to ``mount`` and ``umount2`` from Python.

1.0.0
=====

First release with main functions of the package.

Features
--------

- Implemented ``mount`` function.
- Implemented ``umount`` function.
- Implemented ``MountFlag`` and ``UmountFlag`` enums.
