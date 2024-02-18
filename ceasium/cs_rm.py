import argparse
import os


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Description of your script.')
        parser.add_argument('o_files', nargs='+')
        parser.add_argument('--rm', nargs='+')
        args = parser.parse_args()
        rm = set(args.rm)
        result = [
            o_file for o_file in args.o_files
            if os.path.basename(o_file) not in rm
        ]
        print(result)
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()
