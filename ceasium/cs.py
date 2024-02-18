import json
from multiprocessing import Pool
import os
from os import walk
from os.path import abspath, join, getmtime, basename
from subprocess import run
import subprocess
import sys
import pkgconfig


def get_vars(value):
    start_index = 0
    vars = []
    while start_index < len(value):
        if value[start_index] == '$':
            end_index = start_index + 1
            if value[start_index + 1] == "(":
                indent = 0
                while end_index < len(value):
                    if value[end_index] == "(":
                        indent += 1
                    if value[end_index] == ")" and indent == 1:
                        break
                    end_index += 1
                vars.append(value[start_index:end_index+1])
                start_index = end_index
            else:
                while end_index < len(value):
                    if value[end_index] == " ":
                        break
                    end_index += 1
                vars.append(value[start_index:end_index])
                start_index = end_index
        start_index += 1
    return vars


def resolve(value):
    for var in get_vars(value):
        val = os.environ.get(var[1:])
        if val:
            value = value.replace(var, val)
        elif var.startswith("$(") and var.endswith(")"):
            var_resolved = var.replace(var, resolve(var[2:-1]))
            o = subprocess.run(
                f'{var_resolved}',
                text=True,
                capture_output=True,
                shell=True
            )
            value = value.replace(var, o.stdout.strip())
        else:
            value = value.replace(var, "")
    return value


def get_libs(libs):
    return fix_args(pkgconfig.libs(" ".join(libs)))


def get_c_flags(libs):
    return fix_args(pkgconfig.cflags(" ".join(libs)))


def fix_args(libs):
    flags = libs.split(" -")
    if len(flags) > 1:
        flags = [flags[0]] + [f"-{lib}" for lib in flags[1:]]
    true_flags = []
    symbols = ["-L", "-I"]
    for flag in flags:
        flag = flag.strip()
        is_path = False
        for symbol in symbols:
            if flag.startswith(symbol):
                true_flags.append(f"{symbol}{abspath(flag[2:])}")
                is_path = True
                break
        if not is_path:
            true_flags.append(flag)
    return " ".join(set(true_flags))


def get_mod_time(src_path, c_flags, cc):
    includes_output = run(
        " ".join([cc, *c_flags, "-M", "-H", src_path]),
        shell=True,
        capture_output=True,
        universal_newlines=True
    )
    if includes_output.returncode != 0:
        raise Exception(includes_output.stderr)
    includes = set([
        true_include
        for include in includes_output.stdout.split("\n")
        for true_include in include.split(" ")
        if os.path.exists(true_include) and os.path.isfile(true_include)
    ])
    return max(getmtime(include) for include in includes)


def replace_file_extension(filename, new_extension):
    base_name, _ = os.path.splitext(filename)
    new_filename = base_name + new_extension
    return new_filename


def changed(cc, src_path, o_path, c_flags):
    c_file_paths = [
        abspath(join(root, file))
        for root, _, files in walk(src_path)
        for file in files
        if file.endswith('.c')
    ]
    files = []
    for c_file_path in c_file_paths:
        mod_time = get_mod_time(
            c_file_path,
            c_flags,
            cc
        )
        o_file_path = join(
            o_path,
            replace_file_extension(basename(c_file_path), ".o")
        )
        if not os.path.exists(o_file_path) or mod_time > os.path.getmtime(o_file_path):
            files.append(c_file_path)
    return " ".join(files)


def compile(cc, c_flags, c_file_paths, o_file_dir_path):
    if not os.path.exists(o_file_dir_path):
        os.makedirs(o_file_dir_path)
    arguments = [
        f"{cc} {c_flags} -c {c_file_path} -o {join(o_file_dir_path, )}"
        for c_file_path in c_file_paths.split(" ")
    ]
    result = []
    with Pool() as pool:
        result = pool.map(execute_command, arguments)
    for r in result:
        print(r.args)
        print(r.stderr)
        print(r.stdout)
    return result


def execute_command(cmd):
    return run(cmd, shell=True, capture_output=True, universal_newlines=True)


def run_compile(cc, flags, files, o):
    compile(
        cc,
        os.environ.get(flags),
        os.environ.get(files),
        o
    )


def main():
    if sys.argv[1] == "run":
        with open("C:\\Projects\\game-engine\\build.json") as f:
            config = json.loads(f.read())
            os.environ["libs"] = " ".join(config["libs"].keys())
            for var in list(config['vars'].keys()):
                os.environ[var] = resolve(config['vars'][var])
            cmd = resolve(config["scripts"][sys.argv[2]])
            run(cmd)
    if sys.argv[1] == "ldflags":
        print(get_libs(sys.argv[2:]))
    if sys.argv[1] == "cflags":
        print(get_c_flags(sys.argv[2:]))
    if sys.argv[1] == "changed":
        print(
            changed(
                sys.argv[2],
                sys.argv[3],
                sys.argv[4],
                sys.argv[5:]
            )
        )
    if sys.argv[1] == "compile":
        run_compile(
            sys.argv[2],
            sys.argv[3],
            sys.argv[4],
            sys.argv[5]
        )
    return 0


if __name__ == "__main__":
    main()
