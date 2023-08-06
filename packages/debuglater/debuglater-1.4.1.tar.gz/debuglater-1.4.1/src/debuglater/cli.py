import sys

from debuglater import __version__
from debuglater.pydump import debug_dump


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description=(f"debuglater {__version__}: "
                     "post-mortem debugging for Python programs"))
    debugger_group = parser.add_mutually_exclusive_group(required=False)
    debugger_group.add_argument(
        "--pdb",
        action="store_const",
        const="pdb",
        dest="debugger",
        help="Use builtin pdb or pdb++",
    )
    debugger_group.add_argument(
        "--pudb",
        action="store_const",
        const="pudb",
        dest="debugger",
        help="Use pudb visual debugger",
    )
    debugger_group.add_argument(
        "--ipdb",
        action="store_const",
        const="ipdb",
        dest="debugger",
        help="Use ipdb IPython debugger",
    )
    parser.add_argument("filename", help="dumped file")
    args = parser.parse_args()
    if not args.debugger:
        args.debugger = "pdb"

    print("Starting %s..." % args.debugger, file=sys.stderr)
    dbg = __import__(args.debugger)
    return debug_dump(args.filename, dbg.post_mortem)


if __name__ == "__main__":
    sys.exit(main() or 0)
