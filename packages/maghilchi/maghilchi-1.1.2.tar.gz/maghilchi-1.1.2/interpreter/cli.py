
import argparse


def construct_parser() -> argparse.ArgumentParser:
    """Returns the cli argument parser"""
    parser = argparse.ArgumentParser(
        "maghilchi", description="CLI for the maghilchi interpreter"
    )

    parser.add_argument(
        "filepath",
        help="The path of the maghilchi file to be run",
    )

    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enables the interpreter debug mode"
    )

    parser.add_argument(
        "--compile", "-c", nargs=1, default="True", help="Enables the bytecode compiler"
    )

    parser.add_argument(
        "--compiled-format",
        "-f",
        choices=["pickle", "json"],
        default="pickle",
        help="Specifies the format of the bytecode-compiled file",
    )
    parser.add_argument(
        "--iterations",
        "-i",
        default=1,
        type=int,
        help="Specifies how often the script should be executed",
    )
    
    parser.add_argument(
        "--IDLE", "-ide", default="True", help="Enables the Editor"
    )
    
    return parser
