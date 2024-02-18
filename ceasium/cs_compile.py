import argparse
from multiprocessing import Pool
from subprocess import run
import os
import sys


def compile(cc, c_flags, c_file_paths, o_file_dir_path):
    start_dir = os.getcwd()
    os.chdir(o_file_dir_path)
    arguments = [
        f"{cc} {c_flags} {c_file_path}"
        for c_file_path in c_file_paths
    ]
    result = []
    with Pool() as pool:
        result = pool.starmap(execute_command, arguments)
    os.chdir(start_dir)
    return result


def execute_command(cmd):
    return run(cmd, shell=True, capture_output=True, universal_newlines=True)


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Description of your script.')
        parser.add_argument('cc')
        parser.add_argument('files')
        parser.add_argument('flags')
        parser.add_argument('o')
        args = parser.parse_args()
        compile(
            args.cc,
            os.environ.get(args.flags),
            os.environ.get(args.files),
            args.o
        )
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()
