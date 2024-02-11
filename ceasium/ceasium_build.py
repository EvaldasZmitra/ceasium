import os
import time
from .ceasium_config import read_config
from .ceasium_build_o import build_o_files
from .ceasium_system_util import colors, print_blue, print_green, print_red, run_command, run_gcc_command
from .ceasium_build_common import gen_compiler_flags, gen_linker_flags

build_folder_name = "build"


def build_archive(build_path, o_files, build_config):
    library_path = os.path.join(build_path, f"lib{build_config['name']}.a")
    command = f'ar rcs {library_path} {" ".join(o_files)}'
    run_command(command)


def build_tests(build_path, o_files, build_config):
    result_path = os.path.join(build_path, "tests.exe")
    cc = build_config["compiler"]
    cc_flags = gen_compiler_flags(build_config)
    o_files = " ".join(o_files)
    linker_flags = gen_linker_flags(build_config)
    command = f'{cc} {cc_flags} {o_files} -o {result_path} {linker_flags}'
    run_command(command)


def build_exe(build_path, o_files, build_config):
    result_path = os.path.join(build_path, build_config["name"] + ".exe")
    cc = build_config["compiler"]
    cc_flags = f"{os.linesep}".join(gen_compiler_flags(build_config))
    o_files = f"{os.linesep}".join(o_files)
    linker_flags = f"{os.linesep}".join(gen_linker_flags(build_config))
    sum = [
        cc, os.linesep,
        colors.YELLOW,
        cc_flags, os.linesep,
        colors.RESET,
        colors.DARK_GREY,
        o_files, os.linesep,
        colors.RESET,
        colors.CYAN,
        linker_flags, os.linesep,
        colors.RESET,
        "-o ", result_path, os.linesep,
    ]
    command = "".join(sum)
    print_blue(f"{os.linesep}Building executable...")
    run_gcc_command(command)


def build_dll(build_path, o_files, build_config):
    result_path = os.path.join(build_path, build_config["name"] + ".dll")
    cc = build_config["compiler"]
    cc_flags = gen_compiler_flags(build_config) + " -shared"
    o_files = " ".join(o_files)
    linker_flags = gen_linker_flags(build_config)
    command = f'{cc} {cc_flags} {o_files} -o {result_path} {linker_flags}'
    run_command(command)


def build(args):
    start = time.time()
    try:
        build_config = read_config(args.path)
        build_path = os.path.join(args.path, build_folder_name)
        o_files = build_o_files(args.path, build_config, "src")
        if build_config["type"] == "so":
            build_archive(build_path, o_files, build_config)
        if build_config["type"] == "exe":
            build_exe(build_path, o_files, build_config)
        if build_config["type"] == "dll":
            build_dll(build_path, o_files, build_config)
        print_green(f"Build succeeded in {round(time.time() - start, 2)}s.")
    except Exception as exception:
        print(exception)
        print_red(f"Build failed in {round(time.time() - start, 2)}s.")
