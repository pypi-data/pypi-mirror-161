import sys
from argparse import ArgumentParser

from . import restapi


class register:
    """
    A simple decorator to register sub parsers, but also
    acts as a singelton. Get a list of sub parsers by
    calling ``register.subparsers`` from the ``main`` function
    """

    subparsers = []

    @classmethod
    def subparser(cls, w):
        cls.subparsers.append(w)
        return w


@register.subparser
def setup_rest_api(subparsers):
    setup_rest_api_v1(subparsers, "serve-api", "REST API latest version")
    setup_rest_api_v1(
        subparsers, "serve-api-v1", "REST API v1 (this is the latest version)"
    )


def setup_rest_api_v1(subparsers, name, help):
    """
    Sub parser for the ``serve-api`` argument.
    """
    parser = subparsers.add_parser(name, help=help)
    # parser.add_argument("name", type=str, default="default", help="installation name")
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=str,
        default="./work/adop.ini",
        help="Path to config [default: ./work/adop.ini]",
    )
    parser.add_argument(
        "-b",
        "--bind",
        dest="host",
        type=str,
        default="",
        help="Specify alternate bind address [default: 127.0.0.1]",
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        type=int,
        default=0,
        help="Specify alternate port [default: 8000]",
    )
    parser.set_defaults(func=restapi.serve)


def main():
    global_parser = ArgumentParser(add_help=True)
    global_parser.set_defaults(func=None)
    subparsers = global_parser.add_subparsers(
        title="Commands", description="Additional help for commands: {command} --help"
    )

    # get all registered sub parsers and call its function
    for setup in register.subparsers:
        setup(subparsers)

    args = global_parser.parse_args()

    if args.func:
        kwargs = {k: v for k, v in args._get_kwargs() if not k == "func"}
        try:
            args.func(**kwargs)
        except KeyboardInterrupt:
            print("Aborted by user")
    else:
        global_parser.print_help()


if __name__ == "__main__":
    main()
