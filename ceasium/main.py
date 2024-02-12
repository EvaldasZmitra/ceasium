from .commands.build_cmd.build import build
from .commands.clean import clean
from .commands.init import init
from .commands.run import run
from .commands.install import install
from .config import parse_arguments


def main():
    try:
        args = parse_arguments()
        if args.command == "run":
            run(args)
        if args.command == "build":
            build(args)
        if args.command == "clean":
            clean(args)
        if args.command == "init":
            init(args)
        if args.command == "install":
            install(args)
        return 0
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    main()
