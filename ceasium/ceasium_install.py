from .ceasium_config import read_config
from .ceasium_system_util import run_command


def install(args):
    build_config = read_config(args.path)
    for package in build_config["packages"][build_config["package-manager"]]:
        run_command(package)
