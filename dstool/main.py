import argparse
import os

from dstool.common import *
from dstool.core import *

def command_init(arg):
    dsroot_init()

def command_status(arg):
    app = AppCtx()
    candidates = app._list_dataitem()
    candidates = [e.path for e in candidates]
    registered = app.list_registered_paths()

    # set op
    set_can = set(candidates)
    set_reg = set(registered)

    reg_ok = set_reg & set_can
    reg_err = set_reg - set_can
    can_ok = set_can - set_reg
    # REGISTERED
    print(f"[registered] {len(reg_ok)} items")
    for s in sorted(list(reg_ok)):
        print(f'    {s}')
    # CANDIDATE
    print(f"[non-registered] {len(can_ok)} items")
    for s in sorted(list(can_ok)):
        print(f'    {s}')
    # ERR
    if len(reg_err) > 0:
        print("[WARN] following registered item seems to be not dataitem dir")
        print("[WARN] the data was removed?")
        for s in sorted(list(reg_err)):
            print(f'    {s}')

    #print("candidates", candidates)
    #print("registered", registered)
    #print("appdata", app._load_appdata())

def command_register(arg):
    app = AppCtx()
    app.register(arg.datadir)

def command_unregister(arg):
    app = AppCtx()
    app.unregister(arg.datadir)

def command_mark(arg):
    pass
def command_unmark(arg):
    pass
def command_annotate(arg):
    pass
def command_export(arg):
    pass
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

    # コマンドライン引数をパースして対応するハンドラ関数を実行
    args = parser.parse_args()
    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()

if __name__ == "__main__":
    main()
