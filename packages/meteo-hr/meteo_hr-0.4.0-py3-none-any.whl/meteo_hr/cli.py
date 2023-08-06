import argparse
import sys

from .places import PLACES
from . import run


def make_parser():
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("place", nargs="?", type=str)
    parser.add_argument("-l", "--list", action="store_true")
    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.list:
        for name, slug in PLACES:
            print(name)
        return

    if args.place:
        place = args.place.lower()
        if place not in PLACES:
            print(f"Unknown place: {args.place}", file=sys.stderr)
            print("Use `--list` option to show available places.", file=sys.stderr)
            sys.exit(1)
        name, slug = PLACES[place]
        run(name, slug)
        return

    parser.print_usage(sys.stderr)
    print("Please specify a place.", file=sys.stderr)
    sys.exit(1)
