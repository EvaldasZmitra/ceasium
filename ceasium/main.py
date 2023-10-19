from .ceasium_build import build
from .ceasium_clean import clean
from .ceasium_init import init
from .ceasium_install import install
from .ceasium_run import run
from .ceasium_config import parse_arguments


def main():
    args = parse_arguments()
    if args.action == "build":
        build(args)
    if args.action == "clean":
        clean(args)
    if args.action == "init":
        init(args)
    if args.action == "install":
        install(args)
    if args.action == "run":
        run(args)
    # try:
    # except Exception as e:
    #     print(e)


if __name__ == "__main__":
    main()
