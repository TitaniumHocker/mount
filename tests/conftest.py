import pytest

from mount.cli import main, parser


@pytest.fixture(scope="session")
def clirunner():
    def runner(*args):
        return main(parser.parse_args(args))

    return runner
