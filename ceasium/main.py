from .ceasium_build import build
from .ceasium_clean import clean
from .ceasium_init import init
from .ceasium_install import install
from .ceasium_config import parse_arguments


def main():
    try:
        args = parse_arguments()
        if args.command == "build":
            build(args)
        if args.command == "clean":
            clean(args)
        if args.command == "init":
            init(args)
        if args.command == "install":
            install(args)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
