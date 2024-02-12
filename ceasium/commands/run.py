import os
from ..shell import print_blue
from ..system_util import run_command
from ..config import read_config
from ..constants import build_folder_name


def run(args):
    build_path = os.path.join(args.path, build_folder_name)
    build_config = read_config(args.path)
    exe_path = os.path.join(build_path, build_config["name"])
    print_blue(f"Running {exe_path}")
    run_command(exe_path)
