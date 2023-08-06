import argparse
from .__version__ import (
    __version__,
)
from cndversion.cnd_version import CndVersion


def main():
    arguments = _parse_arguments()
    if arguments.version:
        print(__version__)
        return
    cndversion = CndVersion(arguments)
    cndversion.increment()


def _parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('--version', '-v', default=False, action='store_true', help='display the version')
    parser.add_argument('--major', '-M', default=False, action='store_true', help='Increase major version')
    parser.add_argument('--minor', '-m', default=False, action='store_true', help='Increase minor version')
    parser.add_argument('--patch', '-p', default=False, action='store_true', help='Increase patch version')
    parser.add_argument('--folder', '-f', default=False, help='Install version file in FOLDER, related to the current one')

    return parser.parse_args()
