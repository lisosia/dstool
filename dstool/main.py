import argparse
import os

from dstool.common import *

def command_init(arg):
    dsroot_init()

def command_status(arg):
    app = AppCtx()
    print("dataitem", app._list_dataitem())
    print("appdata", app._load_appdata())

def command_register(arg):
    app = AppCtx()
    app.register(arg.datadir)

def command_unregister(arg):
    print("unregister:", arg)

def main():
    parser = argparse.ArgumentParser(description='dstool command')
    subparsers = parser.add_subparsers()
    # [subcommand] init
    parser_add = subparsers.add_parser('init', help='see `register -h`')
    parser_add.set_defaults(handler=command_init)
    # [subcommand] status
    parser_add = subparsers.add_parser('status', help='see `register -h`')
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

    # コマンドライン引数をパースして対応するハンドラ関数を実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()

if __name__ == "__main__":
    main()
