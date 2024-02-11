import os

from ceasium.ceasium_build_common import build_gcc


from .ceasium_system_util import print_blue, run_command, colors
from .ceasium_build_o import build_o_files
from .ceasium_config import read_config

build_folder_name = "build"


def run(args):
    build_path = os.path.join(args.path, build_folder_name)
    build_config = read_config(args.path)
    o_files = build_o_files(args.path, build_config, "src")
    # build_gcc(build_path, o_files, build_config)
    # exe_path = os.path.join(build_path, build_config["name"])
    # print_blue("Running...")
    # run_command(exe_path)
