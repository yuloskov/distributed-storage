#!/usr/bin/env python3

import argparse
import os
import shutil
from .api import upload_file, delete_file

parser = argparse.ArgumentParser(description='CLI for distributed file system')
subparsers = parser.add_subparsers(title='command', dest='command', help='Command to interact with')

init_parser = subparsers.add_parser('init', help='Initializes DFS root')
init_parser.add_argument('dir', default='dfs', nargs='?', help='Directory where to initialize DFS')
init_parser.add_argument('-f', '--force', dest='force', action='store_true', help='Force rm')
init_parser.add_argument('-r', '--repl', dest='repl', action='store_true', help='Start REPL')

repl_parser = subparsers.add_parser('repl', help='Start REPL')

touch_parser = subparsers.add_parser('touch', help='Creates a new file')
touch_parser.add_argument('file', type=str, nargs='+', help='File name to create')

rm_parser = subparsers.add_parser('rm', help='Removes a file/directory from the DFS')
rm_parser.add_argument('file', type=str, nargs='+', help='Files name to remove')

# mv
# mkdir
# rmdir
# ls
# cd


def repl():
    while True:
        print('$', end=' ')
        args = parser.parse_args(input().split(' '))
        main(args, is_cli=False)


def main(args, is_cli=True):
    if is_cli and args.command == 'init':
        print(f'Initialize DFS root at {args.dir}')
        if args.force:
            if os.path.isdir(args.dir):
                shutil.rmtree(args.dir)
            elif os.path.isfile(args.dir):
                os.remove(args.dir)
            os.mkdir(args.dir)
        else:
            raise NotImplementedError()
        with open('.dfsroot', 'w') as file:
            file.write(os.path.abspath(args.dir))

        if args.repl:
            repl()
    else:
        root = open('.dfsroot', 'r').readline()

        def full_path(path):
            while path[0] == '/':
                path = path[1:]
            return os.path.join(root, path)

        if is_cli and args.command == 'repl':
            repl()
        elif args.command == 'touch':
            for file in args.file:
                abs_path = full_path(file)
                rel_path = abs_path[len(root) + 1:]

                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                open(abs_path, 'w')

                upload_file(rel_path, abs_path)
        elif args.command == 'rm':
            for file in args.file:
                abs_path = full_path(file)
                rel_path = abs_path[len(root) + 1:]

                os.remove(abs_path)

                print(abs_path, rel_path)

                delete_file(rel_path)
        else:
            raise NotImplementedError(f'Unknown command {args.command}')


main(parser.parse_args())
