"""Unit tests for the libc wrappers with the libc calls replaced by fakes."""

import ctypes
import errno
from typing import Any

import pytest

from mount import MountFlag, UmountFlag, core


class FakeCall:
    """Stand-in for a libc function: records arguments, optionally fails."""

    def __init__(self, error: int = 0) -> None:
        self.error = error
        self.calls: list[tuple[Any, ...]] = []

    def __call__(self, *args: Any) -> int:
        self.calls.append(args)
        if self.error:
            ctypes.set_errno(self.error)
            return -1
        return 0


def test_mount_encodes_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCall()
    monkeypatch.setattr(core, "_mount", fake)
    core.mount("tmpfs", "/mnt/точка", "tmpfs", 8, "size=1M")
    assert fake.calls == [(b"tmpfs", "/mnt/точка".encode(), b"tmpfs", 8, b"size=1M")]


def test_mount_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCall()
    monkeypatch.setattr(core, "_mount", fake)
    core.mount("src", "/mnt", "ext4")
    assert fake.calls == [(b"src", b"/mnt", b"ext4", 0, None)]


def test_mount_accepts_flag_enum(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCall()
    monkeypatch.setattr(core, "_mount", fake)
    core.mount("src", "/mnt", "ext4", MountFlag.RDONLY)
    core.mount("src", "/mnt", "ext4", MountFlag.NOEXEC | MountFlag.NOSUID)
    assert [call[3] for call in fake.calls] == [1, 10]
    assert all(type(call[3]) is int for call in fake.calls)


def test_mount_raises_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(core, "_mount", FakeCall(errno.EPERM))
    with pytest.raises(PermissionError) as excinfo:
        core.mount("src", "/mnt", "ext4")
    assert excinfo.value.errno == errno.EPERM


@pytest.mark.parametrize(
    ("flags", "expected"),
    [(0, 0), (2, 2), (UmountFlag.MNT_DETACH, 2)],
)
def test_umount_passes_flags(
    monkeypatch: pytest.MonkeyPatch, flags: int | UmountFlag, expected: int
) -> None:
    fake = FakeCall()
    monkeypatch.setattr(core, "_umount", fake)
    core.umount("/mnt", flags)
    assert fake.calls == [(b"/mnt", expected)]
    assert type(fake.calls[0][1]) is int


def test_umount_default_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeCall()
    monkeypatch.setattr(core, "_umount", fake)
    core.umount("/mnt")
    assert fake.calls == [(b"/mnt", 0)]


def test_umount_raises_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(core, "_umount", FakeCall(errno.EINVAL))
    with pytest.raises(OSError) as excinfo:
        core.umount("/mnt")
    assert excinfo.value.errno == errno.EINVAL


def test_libc_prototypes() -> None:
    assert core._mount.argtypes == (
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_ulong,
        ctypes.c_void_p,
    )
    assert core._umount.argtypes == (ctypes.c_char_p, ctypes.c_int)
