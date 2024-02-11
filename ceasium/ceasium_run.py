import os


from .ceasium_system_util import print_blue, run_command, colors
from .ceasium_build_o import build_o_files
from .ceasium_config import read_config

build_folder_name = "build"


def run(args):
    build_path = os.path.join(args.path, build_folder_name)
    build_config = read_config(args.path)
    exe_path = os.path.join(build_path, build_config["name"])
    print_blue(f"Running {exe_path}")
    run_command(exe_path)
