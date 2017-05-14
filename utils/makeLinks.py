#! /usr/bin/env python3
# coding=utf-8

import argparse
import os
import os.path as osp
from collections import namedtuple

Link = namedtuple("Link", ["name", "target"])

def main():
    in_dir, out_dir = parse_args()
    files = get_files_from_subdirs(in_dir)
    make_links(files, out_dir)


def parse_args():
    desc = "Create symlinks from OUT_DIR to all regural files contained in subdirectories of IN_DIR"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("in_dir", metavar="IN_DIR"
                        , help="Subdirectories of IN_DIR will be searched for files")
    parser.add_argument("out_dir", metavar="OUT_DIR"
                        , help="Links will be created in OUT_DIR")
    args = parser.parse_args()
    return (osp.abspath(args.in_dir), osp.abspath(args.out_dir))


def get_files_from_subdirs(path):
    files = []
    for entry in os.listdir(path):
        entry_path = osp.join(path, entry)
        if not entry.startswith(".") and osp.isdir(entry_path):
            files.extend(get_files(entry_path))
    return files


def get_files(path):
    files = []
    for entry in os.listdir(path):
        entry_path = osp.join(path, entry)
        if not entry.startswith(".") and osp.isfile(entry_path) and not osp.islink(entry_path):
            files.append(entry_path)
    return files


def make_links(files, out_dir):
    links = []
    for file in files:
        links.append(Link(name=osp.join(out_dir, osp.basename(file)), target=file))
    for link in links:
        if not osp.exists(link.name):
            print("Creating link {} -> {}".format(link.name, link.target))
            os.symlink(link.target, link.name)
        else:
            print("{} already exists".format(link.name))


if __name__ == "__main__":
    main()
