import argparse
import sys
from tuxpkg import __version__ as VERSION
from tuxpkg import __doc__ as DOC
from tuxpkg import actions


class TuxPkgCommands:
    def __init__(self, parser):
        self.sub_parsers = parser.add_subparsers(
            title="Subcommands",
            description="All tuxpkg is available through one of its subcommands.",
        )

    def add_command(self, name, help=None, aliases=[]):
        command = self.sub_parsers.add_parser(
            name,
            aliases=aliases,
            help=help,
        )
        command.set_defaults(func=getattr(actions, name.replace("-", "_")))
        return command


def main():
    parser = argparse.ArgumentParser(
        prog="tuxpkg",
        description=DOC.strip(),
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
    )
    parser.set_defaults(func=parser.print_usage)

    commands = TuxPkgCommands(parser)

    commands.add_command(
        "get-makefile",
        aliases=["mk"],
        help="Prints the path to the tuxpkg shared makefile. It can be included in a Makefile using a construct like like `$(include $(shell tuxpkg get-makefile))`.",
    )

    commands.add_command(
        "get-debian-rules",
        help="Prints the path to the tuxpkg shared debian/rules. It can be included in a your debian/rules using a construct like like `$(include $(shell tuxpkg get-makefile))`. You just need to set PYBUILD_NAME first.",
    )

    commands.add_command(
        "create-repository",
        aliases=["repo"],
        help="Creates Debian and RPM repository from files in dist/.",
    )

    commands.add_command("release", help="Makes a release")
    commands.add_command("init", help="Initializes a project directory")

    options = parser.parse_args(sys.argv[1:])
    options.func()

    return 0


def run() -> None:
    if __name__ == "__main__":
        sys.exit(main())


run()
