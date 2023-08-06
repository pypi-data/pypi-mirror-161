#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import os
from io import open

import click
import portalocker

def incr(datafile, lockfile):
    version = -1

    with portalocker.Lock(lockfile, "a+") as lockfobj:
        try:
            with open(datafile, "r") as fobj:
                version = int(fobj.read().strip())
        except FileNotFoundError:
            version = 0
        version += 1
        with open(datafile, "w") as fobj:
            fobj.write(str(version))
        
    try:
        os.unlink(lockfile)
    except Exception as error:
        print(error)
        pass

    return version

@click.command()
@click.option("-l", "--lock-file")
@click.argument("build-serial-file", nargs=1, required=True)
def main(build_serial_file, lock_file):
    """Increment the value in the build-serial-file by one.
    """
    dirpath = os.path.dirname(os.path.abspath(build_serial_file))
    if dirpath:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)

    if not lock_file:
        lock_file_name = "." + os.path.basename(build_serial_file) + ".lock"
        lock_file = os.path.abspath(os.path.join(dirpath, lock_file_name))
    lock_file_dirpath = os.path.dirname(lock_file)
    if lock_file_dirpath:
        if not os.path.exists(lock_file_dirpath):
            os.makedirs(lock_file_dirpath, exist_ok=True)

    try:
        version = incr(build_serial_file, lock_file)
        if version > 0:
            print(version)
        else:
            print("unknown exception...")
            os.sys.exit(1)
    except portalocker.exceptions.LockException:
        print("{build_serial_file} file is locked by another program...".format(build_serial_file=build_serial_file))
        os.sys.exit(2)
    except ValueError:
        print("{build_serial_file} file contains illegal content...".format(build_serial_file=build_serial_file))
        os.sys.exit(3)

if __name__ == "__main__":
    main()
