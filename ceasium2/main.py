from json import loads
from argparse import ArgumentParser
from multiprocessing import Pool
import subprocess
from validate2 import PathValidationException, ValidationException, validate, validate_dict
from subprocess import run
from os.path import basename, join, abspath, exists, getmtime, dirname
from os import walk, makedirs
from time import time


def main():
    args = parse_args()
    build_json = read_json_file("./build.json")
    if args.command == "build":
        build_type = args.build_type
        build_key = args.build_key
        validate()
        generate_output(
            build_type,
            build_key,
            build_json
        )

    # validate_build_json_for_build(build_json, args.subcommand)


def get_c_flags(libraries):
    c_flags = []
    if len(libraries) > 0:
        for lib in libraries:
            cmd = f"pkg-config --cflags \"{lib['name']} >= {lib['version']}\""
            pkg = run(cmd, capture_output=True, text=True)
            if pkg.returncode == 0:
                c_flags += pkg.stdout.strip().split(" ")
        return c_flags
    else:
        return []


def generate_output(
    build_type,
    build_key,
    build_json
):
    obj_keys = build_json["outs"][build_type][build_key]["objs"]
    args = []
    for obj_key in obj_keys:
        obj = build_json["objs"][obj_key]
        cc = obj["cc"]
        libs = [build_json["libs"][lib] for lib in obj['libs']]
        c_flags = obj["cflags"] + get_c_flags(libs)
        c_file_paths = [
            join(root, file)
            for root, _, files in walk(join(".", obj_key))
            for file in files
            if file.endswith('.c')
        ]
        for c_file_path in c_file_paths:
            arg = (cc, c_flags, join(".", "build", obj_key), c_file_path)
            args.append(arg)
    with Pool() as pool:
        return pool.starmap(compile_file, args)


def compile_file(cc, c_flags, o_folder, c_file_path):
    o_file_name = basename(c_file_path).replace(".c", ".o")
    o_file_path = join(o_folder, o_file_name)
    if not exists(dirname(o_file_path)):
        makedirs(dirname(o_file_path))
    mod_time = max([
        getmtime(c_file_path),
        *[getmtime(key) for key in get_includes(c_file_path, c_flags, cc)]
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
    if not exists(o_file_path) or mod_time > getmtime(o_file_path):
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
        abspath(include.lstrip('.').strip())
        for include in includes.split('\n')
        if include.startswith(".")
    ])


def get_output(command):
    return run(
        " ".join(command),
        shell=True,
        capture_output=True,
        universal_newlines=True
    ).stdout


def run_timed(command):
    start = time()
    o = run(
        " ".join(command),
        shell=True,
        capture_output=True,
        universal_newlines=True
    )
    if o.returncode != 0:
        raise Exception(o.stderr)
    run_command(" ".join(command))
    return {
        "result": o.stderr,
        "time": time() - start,
    }


def run_command(command):
    result = ""
    for l in execute(command):
        try:
            result += l
        except Exception as e:
            pass
    return result


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def parse_args():
    parser = ArgumentParser(description="Ceasium build system.")
    subparsers = parser.add_subparsers(
        dest="command",
        help="Pick a command to run."
    )
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument(
        "build_type",
        choices=["exe", "dyn", "static"],
        help="Build type."
    )
    build_parser.add_argument(
        "build_key",
        help="Build key."
    )
    args = parser.parse_args()
    return args


def read_json_file(file):
    with open(file, 'r') as f:
        return loads(f.read())


if __name__ == "__main__":
    main()
    # try:
    #     main()
    # except Exception as e:
    #     print(e)
