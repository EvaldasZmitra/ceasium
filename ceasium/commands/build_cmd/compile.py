from multiprocessing import Pool
import os
from os.path import join
from .get_flags import gen_pkg_config_cc_flags
from ...system_util import ensure_directory_exists, get_output, run_timed
from ...constants import build_folder_name, o_folder_name, src_folder_name


def compile(root_path, libraries, cc_flags, cc):
    o_dir_path = os.path.join(root_path, build_folder_name, o_folder_name)
    ensure_directory_exists(o_dir_path)
    cc_flags = [
        *gen_pkg_config_cc_flags(libraries),
        *cc_flags,
        f"-I{os.path.join(root_path, 'include')}"
    ]
    c_file_paths = [
        join(root, file)
        for root, _, files in os.walk(src_folder_name)
        for file in files
        if file.endswith('.c')
    ]
    arguments = [
        (cc, cc_flags, o_dir_path, c_file_path)
        for c_file_path in c_file_paths
    ]
    with Pool() as pool:
        return pool.starmap(compile_file, arguments)


def compile_file(cc, c_flags, o_folder, c_file_path):
    o_file_name = os.path.basename(c_file_path).replace(".c", ".o")
    o_file_path = os.path.join(o_folder, o_file_name)
    mod_time = max([
        os.path.getmtime(c_file_path),
        *[os.path.getmtime(key) for key in get_includes(c_file_path, c_flags, cc)]
    ])
    return {
        "c_file": c_file_path,
        "o_file": o_file_path,
        **run_compile(
            cc,
            c_flags,
            c_file_path,
            o_file_path,
            mod_time
        )
    }


def run_compile(cc, c_flags, c_file, o_file_path, mod_time):
    if not os.path.exists(o_file_path) or mod_time > os.path.getmtime(o_file_path):
        command = [cc, *c_flags, "-c", c_file, "-o", o_file_path]
        result = run_timed(command)
        return {
            "was_built": True,
            "command": command,
            "result": result['result'],
            "time": result['time'],
        }
    return {
        "was_built": False
    }


def get_includes(src_path, c_flags, cc):
    includes = get_output([cc, *c_flags, "-M", "-H", src_path])
    return set([
        os.path.abspath(include.lstrip('.').strip())
        for include in includes.split('\n')
        if include.startswith(".")
    ])
