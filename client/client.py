#!/usr/bin/env python3

import argparse
import os
import shutil
from subprocess import check_output

from api import upload_file, delete_file, move_file, delete_dir

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

mv_parser = subparsers.add_parser('mv', help='Removes a file/directory from the DFS')
mv_parser.add_argument('src', type=str, help='Src file')
mv_parser.add_argument('dest', type=str, help='Dest file')

mkdir_parser = subparsers.add_parser('mkdir', help='Creates a new directory')
mkdir_parser.add_argument('-p', dest='parent', action='store_true', help='Create parent dirs as well')
mkdir_parser.add_argument('dir', type=str, help='Dir name')

rmdir_parser = subparsers.add_parser('rmdir', help='Removes an existing directory')
rmdir_parser.add_argument('-f', '--force', dest='force', action='store_true',
                          help='Force the deletion, even if a directory contains files')
rmdir_parser.add_argument('dir', type=str, help='Dir name')

ls_parser = subparsers.add_parser('ls', help='Lists files in the current directory')
ls_parser.add_argument('-l', dest='verbose', action='store_true', help='Verbose')
ls_parser.add_argument('dir', type=str, help='Dir name')

cd_parser = subparsers.add_parser('cd', help='Changes working directory')
cd_parser.add_argument('dir', type=str, help='Dir name')

# sync

root = ''
cwd = ''


def full_path(path, root=root):
    while path[0] == '/':
        path = path[1:]
    return os.path.join(root, path)


def repl():
    global cwd

    cwd = root
    while True:
        print(f'{cwd[len(root):]}$', end=' ')
        args = parser.parse_args(input().split(' '))
        print(args)
        main(args, is_cli=False)


def main(args, is_cli=True):
    global root
    global cwd

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

        root = open('.dfsroot', 'r').readline()
        if args.repl:
            repl()
    else:
        root = open('.dfsroot', 'r').readline()

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
        elif args.command == 'mv':
            os.rename(full_path(args.src), full_path(args.dst))
            move_file(args.src, args.dst)
        elif args.command == 'mkdir':
            if args.parent:
                os.makedirs(full_path(args.dir), exist_ok=True)
            else:
                os.mkdir(full_path(args.dir))
        elif args.command == 'rmdir':
            path = full_path(args.dir)
            if len(os.listdir(path)) == 0:
                os.rmdir(path)
            elif not args.force:
                print(f'Dir {args.dir} contains files, are you sure you want to prune it (y/n):')
                if input() not in ['yes', 'YES', 'y']:
                    print('Abort')
                    return
            shutil.rmtree(path)
            delete_dir(args.dir)
        elif args.command == 'ls':
            out = check_output(f'ls {"-la" if args.force else "-a"}{full_path(args.dir)}')
            print(out)
        elif args.command == 'cd':
            cwd = full_path(args.dir, cwd)
            if len(cwd) < len(root):
                raise ValueError('Out of the root directory')
        else:
            raise NotImplementedError(f'Unknown command {args.command}')


main(parser.parse_args())
