"""Shared fixtures: privilege gate for tests that perform real mounts."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

from mount import UmountFlag, umount

#: Set to make missing privileges a failure instead of a skip (used in CI).
REQUIRE_ROOT_ENV = "MOUNT_TESTS_REQUIRE_ROOT"


@pytest.fixture(autouse=True)
def _require_root(request: pytest.FixtureRequest) -> None:
    """Skip (or fail, if required) ``root`` tests when not running as root."""
    if request.node.get_closest_marker("root") is None or os.geteuid() == 0:
        return
    reason = "needs root; run under `unshare -rm` or `sudo unshare -m`"
    if os.environ.get(REQUIRE_ROOT_ENV):
        pytest.fail(reason)
    pytest.skip(reason)


@pytest.fixture
def mountpoint(tmp_path: Path) -> Iterator[Path]:
    """Empty directory that is lazily unmounted on teardown if still mounted."""
    target = tmp_path / "mnt"
    target.mkdir()
    yield target
    if target.is_mount():
        umount(str(target), UmountFlag.MNT_DETACH)
