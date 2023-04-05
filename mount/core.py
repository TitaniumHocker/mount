from ctypes import CDLL, c_char_p, c_int, c_ulong, c_void_p, get_errno
from ctypes.util import find_library
from os import strerror

from .flags import MountFlag, UmountFlag

_sharedlib = find_library("c")
if _sharedlib is None:
    raise ImportError("Failed to find shared library for libc(glibc or musl).")
_libc = CDLL(_sharedlib, use_errno=True)

_mount = _libc.mount
_mount.restype = c_int
_mount.argtypes = (c_char_p, c_char_p, c_char_p, c_ulong, c_void_p)

_umount = _libc.umount2
_umount.restype = c_int
_umount.argtypes = (c_char_p, c_int)


def mount(
    source: str,
    target: str,
    fstype: str,
    flags: int | MountFlag = 0,
    data: str | None = None,
):
    """Mount filesystem.

    :param source: Device/source to mount.
    :param target: Mountpoint.
    :param fstype: Filesystem type. Available filesystem types can be found in /proc/filesystems.
    :param flags: Mount flags.
    :param data: Mount options for specified filesystem.
    :raises OSError: If mount call failed with nonzero return code.
    """
    if (
        _mount(
            source.encode(),
            target.encode(),
            fstype.encode(),
            flags.value if isinstance(flags, MountFlag) else flags,
            data.encode() if data is not None else data,
        )
        != 0
    ):
        raise OSError(get_errno(), strerror(get_errno()))


def umount(target: str, flags: int | UmountFlag = 0):
    """Unmount filesystem.

    :param target: Mountpoint.
    :param flags: Umount flags.
    :raises OSError: If umount2 call failed with nonzero return code.
    """
    if (
        _umount(
            target.encode(),
            flags.value if isinstance(flags, UmountFlag) else flags,
        )
        != 0
    ):
        raise OSError(get_errno(), strerror(get_errno()))
