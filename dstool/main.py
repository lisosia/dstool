import argparse
import os

from dstool.common import *
from dstool.core import *

def command_init(arg):
    dsroot_init()

def command_status(arg):
    app = AppCtx()
    app.status()

def command_register(arg):
    app = AppCtx()
    app.register(arg.datadir)

def command_unregister(arg):
    app = AppCtx()
    app.unregister(arg.datadir)

def command_mark(arg):
    app = AppCtx()
    app.mark(arg.datadir, arg.markname)

def command_unmark(arg):
    app = AppCtx()
    app.unmark(arg.datadir, arg.markname)

def command_annotate(arg):
    app = AppCtx()
    app.annotate(arg.datadir)

def command_export(arg):
    app = AppCtx()
    app.export()

def command_train(arg):
    pass
def command_auto_annotate(arg):
    pass

def main():
    parser = argparse.ArgumentParser(description='dstool command')
    subparsers = parser.add_subparsers()
    # [subcommand] init
    parser_add = subparsers.add_parser('init', help='see `init -h`')
    parser_add.set_defaults(handler=command_init)
    # [subcommand] status
    parser_add = subparsers.add_parser('status', help='see `status -h`')
    parser_add.add_argument('-v', '--verbose', action='store_true', help='verbose')
    parser_add.set_defaults(handler=command_status)
    # [subcommand] register
    parser_add = subparsers.add_parser('register', help='see `register -h`')
    parser_add.add_argument('datadir', help='data dir')
    parser_add.set_defaults(handler=command_register)
    # [subcommand] unregister
    parser_add = subparsers.add_parser('unregister', help='see `unregister -h`')
    parser_add.add_argument('datadir', help='data dir')
    parser_add.set_defaults(handler=command_unregister)
    # [subcommand] mark
    parser_add = subparsers.add_parser('mark', help='see `mark -h`')
    parser_add.add_argument('datadir', help='data dir')
    parser_add.add_argument('markname', help='mark name')
    parser_add.set_defaults(handler=command_mark)
    # [subcommand] unmark
    parser_add = subparsers.add_parser('unmark', help='see `unmark -h`')
    parser_add.add_argument('datadir', help='data dir')
    parser_add.add_argument('markname', help='mark name')
    parser_add.set_defaults(handler=command_unmark)
    # [subcommand] annotate
    parser_add = subparsers.add_parser('annotate', help='see `annotate -h`')
    parser_add.add_argument('datadir', help='data dir')
    parser_add.set_defaults(handler=command_annotate)
    # [subcommand] export
    parser_add = subparsers.add_parser('export', help='see `export -h`')
    parser_add.set_defaults(handler=command_export)

    # コマンドライン引数をパースして対応するハンドラ関数を実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()

if __name__ == "__main__":
    main()
