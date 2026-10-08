"""End-to-end tests performing real mounts.

They need CAP_SYS_ADMIN, so they are skipped unless running as root. The
intended way to run them is inside a private mount namespace, which keeps the
host mount table untouched even if a test fails halfway::

    unshare -rm uv run pytest         # unprivileged, via a user namespace
    sudo unshare -m .venv/bin/pytest  # real root
"""

import errno
from pathlib import Path

import pytest

from mount import MountFlag, UmountFlag, mount, umount

pytestmark = pytest.mark.root


def mount_options(target: Path) -> set[str]:
    """Return mount options of ``target`` as listed in /proc/self/mounts."""
    for line in Path("/proc/self/mounts").read_text().splitlines():
        _, mountpoint, _, options, *_ = line.split()
        if mountpoint == str(target):
            return set(options.split(","))
    raise AssertionError(f"{target} is not mounted")


def test_mount_and_umount(mountpoint: Path) -> None:
    mount("tmpfs", str(mountpoint), "tmpfs")
    assert mountpoint.is_mount()
    (mountpoint / "file").write_text("data")

    umount(str(mountpoint))
    assert not mountpoint.is_mount()
    assert list(mountpoint.iterdir()) == []


def test_mount_data_is_passed_to_filesystem(mountpoint: Path) -> None:
    mount("tmpfs", str(mountpoint), "tmpfs", data="size=64k,mode=700")
    options = mount_options(mountpoint)
    assert "size=64k" in options
    assert "mode=700" in options


def test_mount_flags_are_applied(mountpoint: Path) -> None:
    flags = MountFlag.RDONLY | MountFlag.NOEXEC | MountFlag.NOSUID | MountFlag.NODEV
    mount("tmpfs", str(mountpoint), "tmpfs", flags)
    assert {"ro", "noexec", "nosuid", "nodev"} <= mount_options(mountpoint)
    with pytest.raises(OSError) as excinfo:
        (mountpoint / "file").write_text("data")
    assert excinfo.value.errno == errno.EROFS


def test_bind_mount(mountpoint: Path, tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "file").write_text("data")

    mount(str(source), str(mountpoint), "", MountFlag.BIND)
    assert (mountpoint / "file").read_text() == "data"

    umount(str(mountpoint))
    assert not (mountpoint / "file").exists()
    assert (source / "file").exists()


def test_remount_read_only(mountpoint: Path) -> None:
    mount("tmpfs", str(mountpoint), "tmpfs")
    (mountpoint / "file").write_text("data")

    mount("tmpfs", str(mountpoint), "tmpfs", MountFlag.REMOUNT | MountFlag.RDONLY)
    assert "ro" in mount_options(mountpoint)
    assert (mountpoint / "file").read_text() == "data"


def test_umount_detach_busy_mountpoint(mountpoint: Path) -> None:
    mount("tmpfs", str(mountpoint), "tmpfs")
    with (mountpoint / "file").open("w"):
        with pytest.raises(OSError) as excinfo:
            umount(str(mountpoint))
        assert excinfo.value.errno == errno.EBUSY

        umount(str(mountpoint), UmountFlag.MNT_DETACH)
        assert not mountpoint.is_mount()


def test_mount_unknown_filesystem(mountpoint: Path) -> None:
    with pytest.raises(OSError) as excinfo:
        mount("none", str(mountpoint), "no-such-filesystem")
    assert excinfo.value.errno == errno.ENODEV
    assert not mountpoint.is_mount()


def test_mount_missing_target(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        mount("tmpfs", str(tmp_path / "missing"), "tmpfs")


def test_umount_not_a_mountpoint(mountpoint: Path) -> None:
    with pytest.raises(OSError) as excinfo:
        umount(str(mountpoint))
    assert excinfo.value.errno == errno.EINVAL
