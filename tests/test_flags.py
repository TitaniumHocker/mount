"""Flag values must match the kernel ABI (linux/mount.h, sys/mount.h)."""

import pytest

from mount import MountFlag, UmountFlag


@pytest.mark.parametrize(
    ("flag", "value"),
    [
        (MountFlag.RDONLY, 0x1),
        (MountFlag.NOSUID, 0x2),
        (MountFlag.NODEV, 0x4),
        (MountFlag.NOEXEC, 0x8),
        (MountFlag.SYNCHRONOUS, 0x10),
        (MountFlag.REMOUNT, 0x20),
        (MountFlag.MANDLOCK, 0x40),
        (MountFlag.DIRSYNC, 0x80),
        (MountFlag.NOSYMFOLLOW, 0x100),
        (MountFlag.NOATIME, 0x400),
        (MountFlag.NODIRATIME, 0x800),
        (MountFlag.BIND, 0x1000),
        (MountFlag.MOVE, 0x2000),
        (MountFlag.REC, 0x4000),
        (MountFlag.SILENT, 0x8000),
        (MountFlag.POSIXACL, 0x10000),
        (MountFlag.UNBINDABLE, 0x20000),
        (MountFlag.PRIVATE, 0x40000),
        (MountFlag.SLAVE, 0x80000),
        (MountFlag.SHARED, 0x100000),
        (MountFlag.RELATIME, 0x200000),
        (MountFlag.KERNMOUNT, 0x400000),
        (MountFlag.I_VERSION, 0x800000),
        (MountFlag.STRICTATIME, 0x1000000),
        (MountFlag.LAZYTIME, 0x2000000),
        (MountFlag.ACTIVE, 0x40000000),
        (MountFlag.NOUSER, 0x80000000),
        (UmountFlag.MNT_FORCE, 0x1),
        (UmountFlag.MNT_DETACH, 0x2),
        (UmountFlag.MNT_EXPIRE, 0x4),
        (UmountFlag.UMOUNT_NOFOLLOW, 0x8),
    ],
)
def test_flag_values(flag: MountFlag | UmountFlag, value: int) -> None:
    assert flag == value


def test_all_flags_are_covered() -> None:
    assert len(MountFlag) == 27
    assert len(UmountFlag) == 4


def test_flags_combine_to_int() -> None:
    assert MountFlag.RDONLY | MountFlag.NOEXEC == 9
