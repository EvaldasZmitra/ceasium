import os
import pkgconfig

from .ceasium_system_util import run_command


def build_exe(build_path, o_files, build_config):
    result_path = os.path.join(build_path, build_config["name"])
    flags = gen_flags(build_config)
    if build_config["type"] == "dll":
        result_path = os.path.join(build_path, f"{build_config["name"]}.dll")
        flags["compiler_flags"].append("-shared")
    cc = build_config["compiler"]
    o_files = " ".join(o_files)
    cc_flags = " ".join(flags["compiler_flags"])
    linker_flags = " ".join(flags["linker_flags"])
    command = f'{cc} {cc_flags} {o_files} {linker_flags} -o {result_path}'
    run_command(command)


def gen_flags(build_config):
    lib_flags = gen_flags_libs(build_config["libraries"])
    extra_flags = gen_flags_extra(build_config)
    unique_flags = set(lib_flags + extra_flags)
    linker_flags = []
    compiler_flags = []
    for flag in unique_flags:
        if flag[0].lower() == 'l':
            linker_flags.append(flag)
        else:
            compiler_flags.append(flag)
    return {
        "linker_flags": ["-" + f for f in linker_flags],
        "compiler_flags": ["-" + f for f in compiler_flags]
    }


def gen_flags_extra(build_config):
    flags = ["g", "Wall", "W"]
    if build_config["WarningsAsErrors"]:
        flags.append("Werror")
    optimization_level = build_config["OptimizationLevel"]
    flags.append(f"O{str(optimization_level)}")
    flags += build_config["flags"]
    return flags


def gen_flags_libs(libraries):
    flags = []
    for library in libraries:
        try:
            lib_flags = pkgconfig.libs(library)
            pkg_config_flags = [s.strip() for s in lib_flags.split(" ")]
            flags += [x[1:] for x in pkg_config_flags if x]
        except Exception as e:
            flags.append("l"+library)
            pass
    return flags
