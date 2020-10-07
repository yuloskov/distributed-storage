#!/usr/bin/env python3

import os
import shutil
import argparse

from termcolor import cprint
from api import upload_file, delete_file, list_files, md5, download_file

parser = argparse.ArgumentParser(description='CLI for distributed file system')
subparsers = parser.add_subparsers(title='command', dest='command', help='Command to interact with')

init_parser = subparsers.add_parser('init', help='Initializes DFS root')
init_parser.add_argument('dir', default='dfs', nargs='?', help='Directory where to initialize DFS')
init_parser.add_argument('-f', '--force', dest='force', action='store_true', help='Force rm')

ls_parser = subparsers.add_parser('ls', help='Lists files in the current directory')
ls_parser.add_argument('-l', dest='verbose', action='store_true', help='Verbose')
ls_parser.add_argument('dir', type=str, default='.', nargs='?', help='Dir name')

push_parser = subparsers.add_parser('push', help='Uploads file to DFS storages')
push_parser.add_argument('path', type=str, nargs='+', help='Files/dirs to upload')

pull_parser = subparsers.add_parser('pull', help='Pulls files from DFS storages')
pull_parser.add_argument('path', type=str, nargs='+', help='Files/dirs to download')


def full_path(path, root, base=None):
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


def main(args):
    if args.command == 'init':
        print(f'Initialize DFS root at {args.dir}')
        if args.force:
            if os.path.isdir(args.dir):
                shutil.rmtree(args.dir)
            elif os.path.isfile(args.dir):
                os.remove(args.dir)
            os.mkdir(args.dir)
        else:
            raise NotImplementedError()
        with open('/tmp/.dfsroot', 'w') as file:
            root = os.path.abspath(args.dir)
            file.write(root)
    else:
        root = open('/tmp/.dfsroot', 'r').readline()

        if args.command == 'ls':
            abs_path = full_path(args.dir, root)
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
        elif args.command == 'push':
            for path in args.path:
                abs_path = full_path(path, root)
                rel_path = abs_path[len(root) + 1:]
                print(f'Uploading {path} ...')

                server_files = list_files(rel_path)
                local_files = list_local_files(rel_path, abs_path)

                for p in local_files:
                    if p in server_files and server_files[p]['hash'] != local_files[p]['hash']:
                        upload_file(p, full_path(p, root, root))
                    elif p not in server_files:
                        upload_file(p, full_path(p, root, root))
                    else:
                        print(f'File {p} is already up-to-date')
                for p in server_files:
                    if p not in local_files:
                        delete_file(p)
        elif args.command == 'pull':
            for path in args.path:
                abs_path = full_path(path, root)
                rel_path = abs_path[len(root) + 1:]
                server_files = list_files(rel_path)
                local_files = list_local_files(rel_path, abs_path)
                for p in server_files:
                    fp = full_path(p, root, root)
                    if p in local_files and local_files[p]['hash'] != server_files[p]['hash'] or p not in local_files:
                        os.makedirs(os.path.dirname(fp), exist_ok=True)
                        download_file(p, fp)
                    else:
                        print(f'File {p} is already up-to-date')
        else:
            raise NotImplementedError(f'Unknown command {args.command}')


main(parser.parse_args())
