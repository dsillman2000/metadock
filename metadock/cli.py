import argparse
from pathlib import Path

from metadock import Metadock, exceptions


def parse_arguments():
    """
    Parse command line arguments for the Metadock CLI.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """

    def _add_selector_argument_group(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        selector_group = parser.add_argument_group("selection criteria")
        selector_group.add_argument(
            "-s",
            "--schematic",
            default=[],
            type=str,
            nargs="+",
            dest="schematic_globs",
            help="Schematic glob(s) to pick up from project directory structure",
        )
        selector_group.add_argument(
            "-t",
            "--template",
            default=[],
            type=str,
            nargs="+",
            dest="template_globs",
            help="Template glob(s) to pick up from project directory structure",
        )
        return parser

    arg_parser = argparse.ArgumentParser(
        prog="metadock", description="Generates and formats Jinja documentation templates from yaml sources."
    )
    arg_parser.add_argument(
        "-p",
        "--project-dir",
        action="store",
        dest="project_dir",
        type=Path,
        help="Project directory containing a .metadock directory.",
        default=Path.cwd(),
    )
    cmd_sub_parsers = arg_parser.add_subparsers(help="Metadock command", dest="command")

    init_parser = cmd_sub_parsers.add_parser(
        "init", help="Initialize a new Metadock project in a folder which does not currently have one."
    )
    validate_parser = cmd_sub_parsers.add_parser(
        "validate", help="Validate the structure of an existing Metadock project."
    )
    build_parser = cmd_sub_parsers.add_parser(
        "build", help="Build a Metadock project, rendering some or all documents."
    )
    build_parser = _add_selector_argument_group(build_parser)
    list_parser = cmd_sub_parsers.add_parser(
        "list", help="List all recognized documents which can be generated from a given selection."
    )
    list_parser = _add_selector_argument_group(list_parser)
    clean_parser = cmd_sub_parsers.add_parser(
        "clean", help="Cleans the generated_documents directory for the Metadock project."
    )

    return arg_parser.parse_args()


def main():
    """Entry point of the Metadock command-line interface.
    Parses command-line arguments and executes the corresponding commands.
    """

    arguments: argparse.Namespace = parse_arguments()

    if arguments.command == "init":
        metadock = Metadock.init(arguments.project_dir)
        print("Initialized new Metadock directory at %s" % metadock.metadock_directory)
        exit(0)

    metadock: Metadock = Metadock(working_directory=arguments.project_dir)

    if arguments.command == "validate":
        validation_result = metadock.validate()
        if validation_result.ok:
            print("Project validation succeeded with %d warnings!" % len(validation_result.warnings))
            print(*("(?) %s" % warning for warning in validation_result.warnings), sep="\n")
            exit(0)
        else:
            print(
                "Project validation failed with %d failures and %d warnings!"
                % (len(validation_result.failures), len(validation_result.warnings))
            )
            print(*("(!) %s" % failure for failure in validation_result.failures), sep="\n")
            print(*("(?) %s" % warning for warning in validation_result.warnings), sep="\n")
            exit(1)

    if arguments.command == "clean":
        metadock.clean()
        print("Cleaned directory: %s" % metadock.project.generated_documents_directory)
        exit(0)

    if arguments.command == "build":
        metadock.build(schematic_globs=arguments.schematic_globs, template_globs=arguments.template_globs)
        print("Build successful!")
        exit(0)

    if arguments.command == "list":
        list_results = metadock.list(schematic_globs=arguments.schematic_globs, template_globs=arguments.template_globs)
        print("List picked up the following content schematics:")
        print(*("- %s" % result for result in list_results), sep="\n")
        exit(0)

    raise exceptions.MetadockException("Unrecognized command: %s" % arguments.command)


if __name__ == "__main__":
    main()
