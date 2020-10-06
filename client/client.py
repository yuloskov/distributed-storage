#!/usr/bin/env python3

import os
import errno
import shutil
import argparse
import sys

from termcolor import cprint
from api import upload_file, delete_file, list_files, md5, download_file

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

mv_parser = subparsers.add_parser('mv', help='Moves a file/directory from source to destination')
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
ls_parser.add_argument('dir', type=str, default='.', nargs='?', help='Dir name')

cd_parser = subparsers.add_parser('cd', help='Changes working directory')
cd_parser.add_argument('dir', type=str, help='Dir name')

push_parser = subparsers.add_parser('push', help='Uploads file to DFS storages')
push_parser.add_argument('path', type=str, nargs='+', help='Files/dirs to upload')

pull_parser = subparsers.add_parser('pull', help='Pulls files from DFS storages')
pull_parser.add_argument('path', type=str, nargs='+', help='Files/dirs to download')

import_parser = subparsers.add_parser('import', help='Imports files from host to DFS local folder')
import_parser.add_argument('host_path', type=str, help='Path to the host dir or file')
import_parser.add_argument('dest_path', type=str, help='Path in the dfs dir or file')

import_parser = subparsers.add_parser('export', help='Exports files from DFS to local folder')
import_parser.add_argument('dfs_path', type=str, help='Path to the dfs dir ot file')
import_parser.add_argument('host_path', type=str, help='Path on the host')

exit_parser = subparsers.add_parser('exit', help='Exit from the repl')

root = ''


def full_path(path, base=None):
    while len(path) > 0 and path[0] == '/':
        path = path[1:]
    if base is None:
        res = os.path.abspath(path)
    else:
        cwd = os.getcwd()
        os.chdir(base)
        res = os.path.abspath(path)
        os.chdir(cwd)
    if len(res) < len(root):
        raise ValueError('Out of the root directory')
    return res


def list_local_files(rel_path, abs_path):
    if os.path.isfile(abs_path):
        return {
            rel_path: {
                'hash': md5(abs_path),
                'file_size': round(os.path.getsize(abs_path)/(1024*1024), 2)
            }
        }
    res = {}
    for dir_path, dir_names, file_names in os.walk(abs_path):
        for file_name in file_names:
            path = os.path.join(dir_path, file_name)
            sub_path = path[len(abs_path) + 1:]
            res[os.path.join(rel_path, sub_path)] = {
                'hash': md5(path),
                'file_size': round(os.path.getsize(path)/(1024*1024), 2)
            }
    return res


def repl():
    while True:
        print(f'{os.getcwd()[len(root):]}$', end=' ')
        try:
            args = parser.parse_args(input().split(' '))
        except BaseException:
            continue
        main(args, is_cli=False)


def copy_file_or_dir(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc:
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else:
            raise


def main(args, is_cli=True):
    global root

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
            root = os.path.abspath(args.dir)
            file.write(root)

        os.chdir(root)
        if args.repl:
            repl()
    else:
        if root == '':
            root = open('.dfsroot', 'r').readline()
        if is_cli:
            os.chdir(root)

        if is_cli and args.command == 'repl':
            repl()
        elif args.command == 'touch':
            for file in args.file:
                abs_path = full_path(file)
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                open(abs_path, 'w')
        elif args.command == 'rm':
            for file in args.file:
                abs_path = full_path(file)
                os.remove(abs_path)
        elif args.command == 'mv':
            os.rename(full_path(args.src), full_path(args.dest))
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
        elif args.command == 'ls':
            abs_path = full_path(args.dir)
            rel_path = abs_path[len(root) + 1:]
            local_files = list_local_files(rel_path, abs_path)
            server_files = list_files(rel_path)

            for p in local_files:
                if p not in server_files:
                    local_files[p]['status'] = 'new'
                elif local_files[p]['hash'] != server_files[p]['hash']:
                    local_files[p]['status'] = 'updated'
                else:
                    local_files[p]['status'] = 'unchanged'
            for p in server_files:
                if p not in local_files:
                    local_files[p] = server_files[p]
                    local_files[p]['status'] = 'deleted'

            tasks = [
                ('new', 'green'),
                ('updated', 'yellow'),
                ('unchanged', 'grey'),
                ('deleted', 'red'),
            ]
            for status, color in tasks:
                first = True
                for p in local_files:
                    file = local_files[p]
                    if file['status'] == status:
                        if first:
                            first = False
                            print(f'{status.capitalize()} files:')

                        if 'modified' in file:
                            s = f'\t{p} - {file["hash"]} - {file["file_size"]}MB - {file["modified"]}'
                        else:
                            s = f'\t{p} - {file["hash"]} - {file["file_size"]}MB'

                        cprint(s, color)
        elif args.command == 'cd':
            os.chdir(full_path(args.dir))
        elif args.command == 'push':
            for path in args.path:
                abs_path = full_path(path)
                rel_path = abs_path[len(root) + 1:]
                print(f'Uploading {path}...')

                server_files = list_files(rel_path)
                local_files = list_local_files(rel_path, abs_path)

                for p in local_files:
                    if p in server_files and server_files[p]['hash'] != local_files[p]['hash']:
                        upload_file(p, full_path(p, root))
                    elif p not in server_files:
                        upload_file(p, full_path(p, root))
                    else:
                        print(f'File {p} is already up-to-date')
                for p in server_files:
                    if p not in local_files:
                        delete_file(p)
        elif args.command == 'pull':
            for path in args.path:
                abs_path = full_path(path)
                rel_path = abs_path[len(root) + 1:]
                server_files = list_files(rel_path)
                local_files = list_local_files(rel_path, abs_path)
                for p in server_files:
                    fp = full_path(p, root)
                    if p in local_files and local_files[p]['hash'] != server_files[p]['hash'] or p not in local_files:
                        os.makedirs(os.path.dirname(fp), exist_ok=True)
                        download_file(p, fp)
                    else:
                        print(f'File {p} is already up-to-date')

        elif args.command == 'import':
            src = args.host_path
            folder_to_copy = os.path.basename(os.path.normpath(src))
            dst = os.path.join(full_path(args.dest_path), folder_to_copy)

            copy_file_or_dir(src, dst)
        elif args.command == 'export':
            src = full_path(args.dfs_path)
            folder_to_copy = os.path.basename(os.path.normpath(src))
            dst = os.path.join(args.host_path, folder_to_copy)

            copy_file_or_dir(src, dst)
        elif args.command == 'exit':
            sys.exit(0)
        else:
            raise NotImplementedError(f'Unknown command {args.command}')


main(parser.parse_args())
