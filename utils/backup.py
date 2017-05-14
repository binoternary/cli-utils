#! /usr/bin/env python3
# coding=utf-8

import argparse
import os.path as osp
import subprocess
import sys


def main():
    args = parse_args()
    validate(args)
    command = get_command(args)
    print("Sync from {} to {}".format(args.src, args.dest))
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout.decode(encoding="UTF-8"))


def parse_args():
    parser = argparse.ArgumentParser(description="Backup data using rsync")
    parser.add_argument("--src", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-n", "--dry-run", action="store_true")
    return parser.parse_args()


def validate(args):
    for dir in (args.src, args.dest):
        if not osp.isdir(dir):
            print("{} is not a directory".format(dir))
            sys.exit(1)


def get_command(args):
    command = ["rsync", "--archive", "--delete", "--human-readable"]
    if args.verbose:
        command.append("--verbose")
    if args.dry_run:
        command.append("--dry-run")
    command.append(args.src)
    command.append(args.dest)
    return command


if __name__ == "__main__":
    main()
