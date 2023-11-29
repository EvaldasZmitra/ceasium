import os
import pkgconfig
from .ceasium_config import read_config
from .ceasium_build_o import build_o_files
from .ceasium_system_util import colors, run_command
from .ceasium_build_common import gen_compiler_flags

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
    cc_flags = gen_compiler_flags(build_config)
    o_files = " ".join(o_files)
    linker_flags = gen_linker_flags(build_config)
    command = f'{cc} {cc_flags} {o_files} -o {result_path} {linker_flags}'
    run_command(command)


def build_dll(build_path, o_files, build_config):
    result_path = os.path.join(build_path, build_config["name"] + ".dll")
    cc = build_config["compiler"]
    cc_flags = gen_compiler_flags(build_config) + " -shared"
    o_files = " ".join(o_files)
    linker_flags = gen_linker_flags(build_config)
    command = f'{cc} {cc_flags} {o_files} -o {result_path} {linker_flags}'
    run_command(command)


def build(args):
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
        print(f"{colors.GREEN}Build succeeded.")
    except Exception as e:
        print(f"{colors.RED}Build failed:{colors.RESET}: {e}.")


def gen_linker_flags(build_config):
    lib_flags = gen_pkg_config_flags(build_config['libraries'])
    explicit_lib_flags = gen_explicit_lib_flags(
        build_config['flags']['linker']
    )
    return lib_flags + " " + explicit_lib_flags


def gen_explicit_lib_flags(libraries):
    return " ".join(libraries)


def gen_pkg_config_flags(libraries):
    cflags = ""
    if len(libraries) > 0:
        for lib in libraries:
            try:
                cflags += " " + pkgconfig.libs(lib)
            except Exception:
                pass
        return cflags
    else:
        return ""
