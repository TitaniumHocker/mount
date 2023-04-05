import functools
import sys
from argparse import ArgumentParser, Namespace

from .core import mount, umount
from .flags import MountFlag, UmountFlag

parser = ArgumentParser(description="Simple sys/mount.h CLI wrapper.")
parser.add_argument("--debug", action="store_true", help="Show traceback.")
parser.add_argument("--verbose", action="store_true", help="Additional logs.")
subparsers = parser.add_subparsers(required=True)

mount_parser = subparsers.add_parser("mount", description="Mount operation")
mount_parser.add_argument("source", help="Device/Source to mount.")
mount_parser.add_argument("target", help="Mountpoint.")
mount_parser.add_argument(
    "fstype",
    help="Filesystem type. Available filesystem types can be found in /proc/filesystems.",
)
mount_parser.add_argument(
    "-f",
    "--flags",
    help="Mount flags. Available: {}".format(
        ", ".join(flag.name for flag in MountFlag)
    ),
)
mount_parser.add_argument("options", default=None, help="Additional mount options.")

umount_parser = subparsers.add_parser("umount", description="Unmount operation.")
umount_parser.add_argument("target", help="Mountpoint.")
umount_parser.add_argument(
    "-f",
    "--flags",
    help="Umount flags. Available: {}".format(
        ", ".join(flag.name for flag in UmountFlag)
    ),
)


def _parse_flags(flags: str, enum: type[MountFlag] | type[UmountFlag]) -> int:
    flag = 0
    for name in map(str.upper, flags.split(",")):
        try:
            flag |= getattr(enum, name)
        except AttributeError:
            print(
                "Unknown mount flag: {}. Available: {}".format(
                    name, ", ".join(flag.name for flag in MountFlag)
                ),
                file=sys.stderr,
            )
            sys.exit(1)
    return flag


def _handle_mount(namespace: Namespace, verbose):
    flags = _parse_flags(namespace.flags, MountFlag) if namespace.flags else 0
    verbose(f"{namespace.flags} = {flags}")
    try:
        mount(
            namespace.source,
            namespace.target,
            namespace.fstype,
            flags,
            namespace.options,
        )
    except Exception as exc:
        if namespace.debug:
            raise
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(
        f"{namespace.source} successfully mounted on {namespace.target} as {namespace.fstype}."
    )


mount_parser.set_defaults(func=_handle_mount)


def _handle_umount(namespace: Namespace, verbose):
    flags = _parse_flags(namespace.flags, UmountFlag) if namespace.flags else 0
    verbose(f"{namespace.flags} = {flags}")
    try:
        umount(namespace.target, flags)
    except Exception as exc:
        if namespace.debug:
            raise
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    print(f"{namespace.target} successfully unmounted.")


umount_parser.set_defaults(func=_handle_umount)


def _make_vervose(enabled: bool = False):
    @functools.wraps(print)
    def printer(*args, **kwargs):
        if "file" not in kwargs:
            kwargs["file"] = sys.stderr
        if enabled:
            print(*args, **kwargs)

    return printer


def main(args: Namespace | None = None):
    namespace: Namespace = args or parser.parse_args()
    verbose = _make_vervose(namespace.verbose)
    verbose(namespace)
    namespace.func(namespace, verbose)
    sys.exit(0)


if __name__ == "__main__":
    main()
