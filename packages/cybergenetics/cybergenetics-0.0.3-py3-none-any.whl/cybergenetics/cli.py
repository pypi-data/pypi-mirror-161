from typing import Any, Callable, List, Optional, Type, NamedTuple
import argparse

from .envs import crn


class Argument(NamedTuple):

    name: str
    action: str = 'store'
    annotation: Optional[Type] = None
    help: Optional[str] = None


class Option(NamedTuple):

    name: str
    shortcut: str
    default: Any
    action: str = 'store'
    annotation: Optional[Type] = None
    help: Optional[str] = None


class App():

    __META_COMMAND__ = 'command'

    def __init__(
        self,
        name: str,
        version: str,
        usage: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        formatter_class: argparse.HelpFormatter = argparse.RawTextHelpFormatter,
    ) -> None:
        self.parser = argparse.ArgumentParser(
            prog=name.lower(),
            usage=usage,
            description=description,
            epilog=epilog,
            formatter_class=formatter_class,
        )
        self.parser.add_argument(
            '-V',
            '--version',
            action='version',
            version=f'%(prog)s {version}',
            help='show the %(prog)s version number and exit',
        )

    def command(
        self,
        func: Callable,
        name: str,
        arguments: List[Argument] = [],
        options: List[Option] = [],
        help: Optional[str] = None,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        formatter_class: argparse.HelpFormatter = argparse.RawTextHelpFormatter,
    ):
        description = help if description is None else description
        if getattr(self, 'subparsers', None) is None:
            self.subparsers = self.parser.add_subparsers(metavar=self.__META_COMMAND__)
        subparser = self.subparsers.add_parser(
            name.lower(),
            help=help,
            description=description,
            epilog=epilog,
            formatter_class=formatter_class,
        )
        subparser.set_defaults(**{self.__META_COMMAND__: func})
        for argument in arguments:
            subparser.add_argument(
                argument.name.lower(),
                action=argument.action,
                type=argument.annotation,
                help=argument.help,
            )
        subparser_group = None
        for option in options:
            subparser_group = subparser.add_argument_group(
                title=f'{subparser.prog} options',
                description=None,
            ) if subparser_group is None else subparser_group
            subparser_group.add_argument(
                option.name.lower(),
                option.shortcut,
                action=option.action,
                type=option.annotation,
                default=option.default,
                help=option.help,
            )

    def run(
        self,
        args: Optional[List[str]] = None,
        namespace: Optional[argparse.Namespace] = None,
    ):
        namespace = self.parser.parse_args(args=args, namespace=namespace)
        args = namespace.__dict__
        command = args.pop(self.__META_COMMAND__, None)
        if command is not None:
            command(**args)


def main():
    app = App(
        name='cybergenetics',
        version='0.0.3',
        description='cybergenetics configuration tool',
    )
    app.command(
        crn.init,
        'init',
        help='generate a configuration template',
        options=[
            Option(
                '--path',
                '-p',
                default='.cybergenetics_cache',
                annotation=str,
                help='path to the configuration template to be generated',
            ),
            Option(
                '--verbose',
                '-v',
                default=False,
                action='store_true',
                annotation=bool,
                help='verbose or not',
            )
        ],
    )
    app.run()


if __name__ == '__main__':
    main()
