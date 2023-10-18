import os
import pkgconfig

from .ceasium_system_util import run_command


def build_exe(build_path, o_files, build_config):
    exe_path = os.path.join(build_path, build_config["name"])
    flags = gen_flags(build_config)
    cc = build_config["compiler"]
    command = f'{cc} {flags} {" ".join(o_files)} -o {exe_path}'
    run_command(command)


def gen_flags(build_config):
    lib_flags = gen_flags_libs(build_config["libraries"])
    extra_flags = gen_flags_extra(build_config)
    return lib_flags + extra_flags


def gen_flags_extra(build_config):
    flags = "-g -Wall -W "
    if build_config["WarningsAsErrors"]:
        flags += "-Werror "
    optimization_level = build_config["OptimizationLevel"]
    flags += f"-O{str(optimization_level)} "
    flags += build_config["flags"]
    return flags


def gen_flags_libs(libraries):
    str = ""
    for library in libraries:
        try:
            lib_flags = pkgconfig.libs(library)
            str += f"{lib_flags} "
        except Exception as e:
            str += f"-l{library} "
            pass
    return str
