import os
import subprocess
import time
import pkgconfig
from multiprocessing import Pool

from .ceasium_system_util import colors, find_files, remove_trailing_backslash, run_command, ensure_directory_exists
from .ceasium_build_common import gen_compiler_flags

build_folder_name = "build"
o_folder_name = "o"


def build_o_files(path, build_config, folder_name):
    src_files = find_files(os.path.join(path, folder_name))
    cmds = []
    o_mod_times = []
    file_pairs = get_src_o_path_pairs(path, src_files, folder_name)
    for (src_path, o_path) in file_pairs:
        src_mod_time = get_src_mod_time(src_path, build_config)
        o_mod_time = get_o_mod_time(o_path)
        if src_mod_time > o_mod_time:
            cmd = gen_build_o_file_cmd(path, src_path, o_path, build_config)
            cmds.append(cmd)
            o_mod_times.append((o_path, src_mod_time))
        else:
            print(f"{colors.BLUE}Unchanged{colors.RESET} {src_path}.")
    ensure_directory_exists(os.path.join(
        path, build_folder_name, o_folder_name))
    pool = Pool()
    pool.map(run_command, cmds)
    for (o_path, mod_max_time) in o_mod_times:
        os.utime(o_path, times=(time.time(), mod_max_time))
    return [o_path for (_, o_path) in file_pairs]


def get_included_files(src_file_path, build_config):
    h_paths = []
    compiler_flags_cmd = [build_config["compiler"], "-MM", src_file_path]
    cmd_result = subprocess.check_output(
        compiler_flags_cmd,
        universal_newlines=True
    )
    cmd_result_lines = cmd_result.splitlines()[1:]
    for s in cmd_result_lines:
        sanitized_path = remove_trailing_backslash(s).strip()
        h_paths.append(sanitized_path)
    return h_paths


def get_src_mod_time(path, build_config):
    h_paths = get_included_files(path, build_config)
    mod_times = [os.path.getmtime(path) for path in h_paths]
    mod_times.append(os.path.getmtime(path))
    return max(mod_times)


def get_o_mod_time(path):
    if os.path.exists(path):
        return os.path.getmtime(path)
    return 0


def get_src_o_path_pairs(path, src_files, folder_name):
    paths = []
    for (src_file_relative_path, src_file_name) in src_files:
        src_path = os.path.join(
            path,
            folder_name,
            src_file_relative_path,
            src_file_name)
        o_path = os.path.join(
            path,
            build_folder_name,
            o_folder_name,
            src_file_name[:-1] + "o")
        paths.append((src_path, o_path))
    return paths


def gen_build_o_file_cmd(path, src_path, o_path, build_config):
    cc = build_config['compiler']
    cc_flags = gen_compiler_flags(build_config)
    includes = create_include_string(path, build_config["libraries"])
    return f"{cc} {cc_flags} {includes} -c {src_path} -o {o_path}"


def create_include_string(path, libraries):
    includes = [f'-I{os.path.join(path, "include")}']
    for library in libraries:
        try:
            includes += pkgconfig.cflags(library).split(" ")
        except Exception as e:
            pass
    return " ".join(set(includes))
