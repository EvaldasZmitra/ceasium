import argparse
import json
import os
import platform
import shutil
import subprocess
import pkgconfig

project_build_file_name = "build.json"
build_folder_name = "build"
src_folder_name = "src"
obj_folder_name = "obj"


def build_static_lib(build_path, o_files, build_config):
    library_path = os.path.join(build_path, f"lib{build_config['name']}.a")
    command = f'ar rcs {library_path} {" ".join(o_files)}'
    run_command(command)


def create_include_string(path, libraries):
    includes = [f'-I{os.path.join(path, "include")}']
    for library in libraries:
        try:
            includes += pkgconfig.cflags(library).split(" ")
        except Exception as e:
            pass
    return " ".join(set(includes))


def build_o_files(path, build_path, build_config):
    src_path = os.path.join(path, src_folder_name)
    src_files = find_files(src_path)
    o_files = []
    includes = create_include_string(path, build_config["libraries"])
    for (src_file_relative_path, src_file_name) in src_files:
        src_file_path = os.path.join(
            src_path,
            src_file_relative_path,
            src_file_name
        )
        o_file_dir = os.path.join(
            build_path,
            obj_folder_name
        )
        ensure_directory_exists(o_file_dir)
        o_file_path = os.path.join(
            o_file_dir,
            src_file_name[:-1] + "o"
        )
        command = f"{build_config['compiler']} -c {
            src_file_path} {includes} -o {o_file_path}"
        run_command(command)
        o_files.append(o_file_path)
    return o_files


def create_lib_string(libraries):
    str = ""
    for library in libraries:
        try:
            lib_flags = pkgconfig.libs(library)
            str += f"{lib_flags} "
        except Exception as e:
            str += f"-l{library} "
            pass
    return str


def build_exe(build_path, o_files, build_config):
    exe_path = os.path.join(build_path, build_config["name"])
    lib_str = create_lib_string(build_config["libraries"])
    flags = "-g -Wall -W "
    if build_config["WarningsAsErrors"]:
        flags += "-Werror "
    optimization_level = build_config["OptimizationLevel"]
    flags += f"-O{str(optimization_level)} "
    command = f'{build_config["compiler"]} {flags} {
        " ".join(o_files)} {lib_str} -o {exe_path}'
    run_command(command)


def build_dynamic_lib(build_path, o_files, build_config):
    library_path = os.path.join(build_path, f"{build_config['name']}.dll")
    command = f'{build_config["compiler"]
                 } -shared -o {library_path} {" ".join(o_files)}'
    run_command(command)


def build(args):
    build_config = read_config(args.path)
    build_path = os.path.join(args.path, build_folder_name)
    o_files = build_o_files(args.path, build_path, build_config)
    if build_config["type"] == "exe":
        build_exe(
            build_path,
            o_files,
            build_config
        )
    if build_config["type"] == "so":
        build_static_lib(
            build_path,
            o_files,
            build_config
        )
    if build_config["type"] == "dll":
        build_dynamic_lib(
            build_path,
            o_files,
            build_config
        )


def clean(args):
    build_path = os.path.join(args.path, build_folder_name)
    shutil.rmtree(build_path)


def init(args):
    src_path = os.path.join(args.path, src_folder_name)
    ensure_directory_exists(src_path)
    ensure_directory_exists(os.path.join(args.path, build_folder_name))
    ensure_directory_exists(os.path.join(args.path, "include"))
    write_if_not_exists(
        os.path.join(args.path, project_build_file_name),
        """
{
  "name": "myapp",
  "compiler": "gcc",
  "type": "exe",
  "WarningsAsErrors": false,
  "OptimizationLevel": 0,
  "libraries": [],
  "package-manager": "pacman",
  "packages": {
    "pacman": [],
    "apt": []
  }
}
"""
    )
    write_if_not_exists(
        os.path.join(src_path, "main.c"),
        """
#include <stdio.h>

int main(int argc, char *argv[])
{
    printf("Hello World!");
}
"""
    )


def install(args):
    build_config = read_config(args.path)
    for package in build_config["packages"][build_config["package-manager"]]:
        run_command(package)


def run(args):
    build_config = read_config(args.path)
    build_path = os.path.join(args.path, build_folder_name)
    exe_path = os.path.join(build_path, build_config["name"])
    run_command(exe_path)


def configure_arg_parser():
    os_name = platform.system()
    parser = argparse.ArgumentParser(
        description="Builds a C project.")
    parser.add_argument(
        'action',
        choices=["init", "build", "install", "run", "clean"],
        type=str
    )
    parser.add_argument(
        "--path",
        type=str,
        help="The root path of the project.",
        default=os.getcwd(),
        required=False)
    parser.add_argument(
        "--package-env",
        type=str,
        help="""
        Package environment defaults to os name [Windows, Linux, Darwin].
        A value can be passed to use different install commands defined in
        build.json. For example - define new env Snap, pass in value Snap and it
        will use snap commands from build.json to install packages.""",
        default=os_name,
        required=False)
    return parser


def parse_arguments():
    parser = configure_arg_parser()
    return parser.parse_args()


def run_command(command):
    print(command)
    for line in execute(command):
        print(line, end="")


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def find_files(base_path, relative_path=""):
    files = []
    path = base_path
    if relative_path != "":
        path = os.path.join(path, relative_path)
    for filename in os.listdir(path):
        added_path = os.path.join(path, filename)
        if os.path.isfile(added_path) and filename[-2:] == ".c":
            files.append((relative_path, filename))
        if os.path.isdir(added_path):
            new_relative_path = os.path.join(relative_path, filename)
            files = files + find_files(base_path, new_relative_path)
    return files


def read_config(file_path):
    build_file_path = os.path.join(file_path, project_build_file_name)
    with open(build_file_path, "r") as file:
        return json.load(file)


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def write_if_not_exists(path, text):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(text)


def main():
    try:
        args = parse_arguments()
        if args.action == "install":
            install(args)
        if args.action == "build":
            build(args)
        if args.action == "run":
            run(args)
        if args.action == "clean":
            clean(args)
        if args.action == "init":
            init(args)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
