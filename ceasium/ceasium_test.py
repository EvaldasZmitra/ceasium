import os


from .ceasium_system_util import run_command, colors

from .ceasium_build import build_tests
from .ceasium_build_o import build_o_files
from .ceasium_config import read_config

build_folder_name = "build"


def test(args):
    build_path = os.path.join(args.path, build_folder_name)
    build_config = read_config(args.path)
    print(f"{colors.GREEN}Building tests...{colors.RESET}")
    o_files_src = build_o_files(args.path, build_config, "src")
    filtered_strings = [s for s in o_files_src if not s.endswith("main.o")]

    o_files_test = build_o_files(args.path, build_config, "tests")
    build_tests(build_path, filtered_strings + o_files_test, build_config)
    exe_path = os.path.join(build_path, "tests.exe")
    print(f"{colors.GREEN}Running tests...{colors.RESET}")
    run_command(exe_path)
