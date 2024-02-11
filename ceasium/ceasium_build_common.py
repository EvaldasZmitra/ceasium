import os
import pkgconfig

from ceasium.ceasium_system_util import colors, print_blue, run_gcc_command


def gen_linker_flags(build_config):
    flags = gen_pkg_config_lib_flags(build_config["libraries"])
    flags += build_config['flags']['linker']
    flags = list(set(flags))
    flags.sort()
    return flags


def gen_compiler_flags(build_config):
    flags = gen_pkg_config_cc_flags(build_config["libraries"])
    flags += build_config['flags']['compiler']
    flags = list(set(flags))
    flags.sort()
    return flags


def gen_pkg_config_lib_flags(libraries):
    libFlags = []
    if len(libraries) > 0:
        for lib in libraries:
            try:
                libFlags += pkgconfig.libs(lib).split(" ")
            except Exception:
                pass
        return libFlags
    else:
        return []


def gen_pkg_config_cc_flags(libraries):
    cflags = []
    if len(libraries) > 0:
        for lib in libraries:
            try:
                cflags += pkgconfig.cflags(lib).split(" ")
            except Exception:
                pass
        return cflags
    else:
        return []


def build_gcc(build_path, o_files, build_config):
    # result_path = os.path.join(build_path, build_config["name"] + ".exe")
    # cc = build_config["compiler"]
    # cc_flags = f"{os.linesep}".join(gen_compiler_flags(build_config))
    # o_files = f"{os.linesep}".join(o_files)
    # linker_flags = f"{os.linesep}".join(gen_linker_flags(build_config))
    # sum = [
    #     cc, os.linesep,
    #     colors.YELLOW,
    #     cc_flags, os.linesep,
    #     colors.RESET,
    #     colors.DARK_GREY,
    #     o_files, os.linesep,
    #     colors.RESET,
    #     colors.CYAN,
    #     linker_flags, os.linesep,
    #     colors.RESET,
    #     "-o ", result_path, os.linesep,
    # ]
    # command = "".join(sum)
    # print_blue(f"{os.linesep}Building executable...")
    # run_gcc_command(command)
    build_gcc_total(
        gen_compiler_flags(build_config),
        gen_linker_flags(build_config),
        o_files,
        build_config["compiler"],
        os.path.join(build_path, build_config["name"])
    )


def join_gcc(s, e, c):
    if len(e) > 0:
        return s + [c] + [e] + [os.linesep] + [colors.RESET]
    return s


def build_gcc_total(compiler_flags, linker_flags, o_files, cc, result_path):
    cc_flags = f"{os.linesep}".join(compiler_flags)
    o_files = f"{os.linesep}".join(o_files)
    linker_flags = f"{os.linesep}".join(linker_flags)
    sum = [cc, os.linesep]
    sum = join_gcc(sum, cc_flags, colors.YELLOW)
    sum = join_gcc(sum, o_files, colors.DARK_GREY)
    sum = join_gcc(sum, linker_flags, colors.CYAN)
    sum += ["-o ", result_path, os.linesep]
    r_dir = os.path.dirname(result_path)
    if not os.path.exists(r_dir):
        os.makedirs(r_dir)
    command = "".join(sum)
    command = command.replace(os.linesep, ' ')
    return run_gcc_command(command)
