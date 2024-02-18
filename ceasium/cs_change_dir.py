import argparse
from os.path import join, basename, abspath


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Description of your script.')
        parser.add_argument('dir')
        parser.add_argument('dirs', nargs='+')
        args = parser.parse_args()
        result = [
            abspath(join(args.dir, basename(o_file))) for o_file in args.dirs
        ]
        print(" ".join(result))
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()
