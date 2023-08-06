import argparse
import inspect

from typing import Callable, Mapping, Optional, Sequence, Set


def create_subparser(
    parser: argparse.ArgumentParser,
    func: Callable,
    short_options: Mapping[str, str] = dict(),
    skip_args: Sequence = list(),
    subparser_name: Optional[str] = None,
    parents: Set[argparse.ArgumentParser] = set(),
) -> argparse.ArgumentParser:
    """
    Given an existing argparse ArgumentParser, and a function to be exposed as
    a command line interface, this function will inspect the passed function
    and build a subparser for it. The intention being that it should reduce
    duplication of argument declaration while making use of tools existing
    in the standard library.

    Parameters
    --------------

    parser: An existing argparse.ArgumentParser instance

    func: A function that you wish to add as a subparser for access from
    commandline

    short_options: A Mapping of argument name to the short option names.

    skip_args: A Sequence of arguments to not build flags and options
    for. Arguments that unpack, like *args, **kwargs, are always skipped..

    subparser_name: Optionally a name to override the function name from
    command line.

    parents: A Set of ArgumentParser classes to add the arguments to the
    subparser. Adds the parser (first argument) as a parent automatically.
    """
    try:
        subparser = [
            action
            for action in parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ][0]
    except IndexError:
        subparser = parser.add_subparsers()

    if subparser.dest == "==SUPPRESS==":
        subparser.dest = "command"

    name = subparser_name or func.__name__
    function_parser = subparser.add_parser(name, parents=parents)

    skip_args = set(skip_args)
    for parent in parents:
        for action in parent._actions:
            if isinstance(action, argparse._StoreAction):
                skip_args.add(action.dest)

    for action in parser._actions:
        if isinstance(action, argparse._StoreAction):
            skip_args.add(action.dest)

    signature = inspect.signature(func)
    for k, v in signature.parameters.items():
        arg_params = dict()
        if k in skip_args or str(v).startswith("*"):
            continue
        if v.default is inspect._empty:
            arg_name = (k,)
        if isinstance(v.annotation, bool):
            if v.default is not inspect._empty:
                arg_params["action"] = "store_false" if v.default else "store_true"
            else:
                arg_params["action"] = "store_true"
        else:
            arg_params["default"] = v.default
            short_option = short_options.get(k)
            if short_option is None:
                arg_name = (f"--{k}",)
            else:
                if not short_option.startswith("-"):
                    short_option = f"-{short_option}"
                arg_name = (short_option, f"--{k}")

        function_parser.add_argument(*arg_name, **arg_params)

    usage = [parser.usage, func.__doc__]

    usage += [p.usage for p in parents]
    usage = [u for u in usage if u is not None]
    function_parser.usage = "\n".join(usage)
    function_parser.set_defaults(func=func)

    return function_parser
