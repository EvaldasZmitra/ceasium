from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import subprocess
import pkgconfig
from multiprocessing import Pool

from .ceasium_system_util import find_files, print_blue, print_green, print_grey, print_red, print_yellow, remove_trailing_backslash
from .ceasium_build_common import build_gcc_total, gen_compiler_flags

build_folder_name = "build"
o_folder_name = "o"


def run_io_tasks_in_parallel(tasks):
    with ThreadPoolExecutor() as executor:
        running_tasks = [executor.submit(task) for task in tasks]
        for running_task in running_tasks:
            running_task.result()


def work(build_config, include_path, src_path, o_path):
    cflags = gen_compiler_flags(build_config)
    cflags += [f"-I{include_path}"]
    includes = get_includes(
        src_path,
        cflags,
        build_config["compiler"]
    )
    m = os.path.getmtime(src_path)
    for key in includes:
        t = os.path.getmtime(key)
        if t > m:
            m = t
    if not os.path.exists(o_path) or m > os.path.getmtime(o_path):
        return build_gcc_total(
            cflags + [f"-c {src_path}"],
            [],
            [],
            build_config["compiler"],
            o_path
        )
    else:
        print_grey(f"Unchanged {src_path}")


def build_o_files(path, build_config, folder_name):
    print_blue(f"Building o files...")
    src_files = find_files(os.path.join(path, folder_name))
    file_pairs = get_src_o_path_pairs(path, src_files, folder_name)
    include_path = os.path.join(path, "include")
    all_args = []
    for (src_path, o_path) in file_pairs:
        all_args.append((build_config, include_path, src_path, o_path))

    with ThreadPoolExecutor() as executor:
        future_to_input = {
            executor.submit(
                work,
                *input_param
            ):
            input_param for input_param in all_args
        }
        for future in as_completed(future_to_input):
            input_param = future_to_input[future]
            try:
                r = future.result()
                if r:
                    (result, time, cmd) = r
                    if result:
                        t = f"Built {input_param[2]} in {round(time, 2)}s:"
                        print_yellow(t)
                        # print(cmd)
                        print(result)
                    else:
                        t = f"Built {input_param[2]} in {round(time, 2)}s."
                        print_green(t)
                        # print(cmd)
            except Exception as e:
                print_red(f"Built {input_param[2]} failed:")
                if e:
                    print(e)

    # flags_inc = cflags + ['-MM', '-H']
    # flags_inc = " ".join(flags_inc)
    # cc = build_config['compiler']
    # include_dirs, flag_includes = get_includes(
    #     src_path,
    #     cflags,
    #     flags_inc,
    #     cc
    # )
    # cflags = [
    #     flag for flag in cflags
    #     if not flag.startswith("-I")
    # ]
    # cflags += [
    #     f"-I{flag}"
    #     for flag in flag_includes.intersection(include_dirs)
    # ]
    # includes = get_included_files(src_path, build_config)
    # print(f"Includes {src_path}:")
    # print(includes)
    # build_gcc_total(
    #     gen_compiler_flags(build_config),
    #     [],
    #     [src_path],
    #     build_config["compiler"],
    #     o_path
    # )
    # print(src_path + " " + o_path)
    # src_mod_time = get_src_mod_time(src_path, build_config)
    # o_mod_time = get_o_mod_time(o_path)
    # if src_mod_time > o_mod_time:
    #     cmd = gen_build_o_file_cmd(path, src_path, o_path, build_config)
    #     cmds.append(cmd)
    #     build_gcc_total(
    #         cflags + [f"-c {src_path}"],
    #         [],
    #         [],
    #         build_config["compiler"],
    #         o_path
    #     )
    # else:
    #     print(f"{colors.DARK_GREY}Unchanged{colors.RESET} {src_path}.")

    # ensure_directory_exists(os.path.join(
    #     path, build_folder_name, o_folder_name))
    # pool = Pool()
    # pool.map(lambda x, cmds)
    # for (o_path, mod_max_time) in o_mod_times:
    #     os.utime(o_path, times=(time.time(), mod_max_time))
    return [o_path for (_, o_path) in file_pairs]


def get_includes(src_path, cflags, cc):
    includes = subprocess.check_output(
        f"{cc} {' '.join(cflags + ['-M', '-H'])} {src_path}",
        stderr=subprocess.STDOUT,
        text=True
    )
    includes = set([
        os.path.abspath(include.lstrip('.').strip())
        for include in includes.split('\n')
        if include.startswith(".")
    ])
    return includes
    # flag_includes = set([
    #     os.path.abspath(flag[2:])
    #     for flag in cflags
    #     if flag.startswith("-I")
    # ])


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
