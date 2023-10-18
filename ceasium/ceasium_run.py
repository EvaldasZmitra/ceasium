import os

from .ceasium_config import read_config
from .ceasium_system_util import run_command


build_folder_name = "build"


def run(args):
    build_config = read_config(args.path)
    build_path = os.path.join(args.path, build_folder_name)
    exe_path = os.path.join(build_path, build_config["name"])
    run_command(exe_path)
