import argparse
import pkgconfig


def main():
    try:
        parser = argparse.ArgumentParser(
            description='Description of your script.')
        parser.add_argument('libs', nargs='+')
        args = parser.parse_args()
        print(pkgconfig.cflags(" ".join(args.libs)))
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()
