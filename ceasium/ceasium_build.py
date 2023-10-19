import os
from .ceasium_config import read_config
from .ceasium_build_o import build_o_files
from .ceasium_build_exe import build_exe
from .ceasium_build_so import build_static_lib

build_folder_name = "build"


def build(args):
    build_config = read_config(args.path)
    build_path = os.path.join(args.path, build_folder_name)
    o_files = build_o_files(args.path, build_config)
    if build_config["type"] == "so":
        build_static_lib(build_path, o_files, build_config)
    else:
        build_exe(build_path, o_files, build_config)
