from multiprocessing import Pool
from json import loads
from subprocess import run
from os.path import abspath, basename, join, exists, getmtime, splitext
from os import walk, makedirs, getcwd
import os
from argparse import ArgumentParser
from shutil import rmtree
from .constants import ldflags_name, type_name, include_name, cflags_name, src_folder_name, build_folder_name, project_build_file_name, include_template, build_config_template, main_template, test_template, git_ignore_template, packages
import platform


class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class PathValidationException(ValidationException):
    def __init__(self, path, message):
        path = make_path(path)
        super().__init__(f"{path} {message}.")


def main():
    args = parse_args()
    if args.command == build_folder_name:
        build()
    if args.command == "run":
        print(cs_run([join(".", build_folder_name, basename(getcwd()))]))
    # if args.command == "install":
    #     install(build_json, args.package_manager)
    if args.command == "clean":
        rmtree(join(".", build_folder_name))
    if args.command == "init":
        init()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


def init():
    ensure_dir_exists(join(".", include_name))
    ensure_dir_exists(join(".", src_folder_name))
    ensure_dir_exists(join(".", "test"))
    with open(join(".", project_build_file_name), "w") as f:
        f.write(build_config_template)
    with open(join(".", src_folder_name, "main.c"), "w") as f:
        f.write(main_template)
    with open(join(".", "test", "main.c"), "w") as f:
        f.write(test_template)
    with open(join(".", ".gitignore"), "w") as f:
        f.write(git_ignore_template)
    with open(join(".", include_name, "main.h"), "w") as f:
        f.write(include_template)


def install(build_json, package_manager):
    return [
        cs_run(packages[lib][package_manager])
        for lib in build_json.get("libs", [])
    ]


def build():
    build_json = read_json_file(project_build_file_name)
    for dir in build_json.get("lib-dirs", []):
        os.environ["PKG_CONFIG_PATH"] = f"{os.environ.get('PKG_CONFIG_PATH')};{
            abspath(dir)}"
    compile(build_json)
    if build_json[type_name] == "exe":
        link(build_json)

    if build_json[type_name] == "dynamic-lib":
        link(build_json)

    if build_json[type_name] == "static-lib":
        create_static_lib(build_json)


def link(build_json):
    ldflags = get_ldflags(build_json)
    name = basename(getcwd())
    extension = ""
    prefix = ""
    if build_json[type_name] == "dynamic-lib":
        create_pkg_conf(
            [
                *ldflags,
                f"-l{name}",
                f"-L{join(getcwd(), 'build')}"
            ],
            [f"-I{join(getcwd(), 'include')}"],
            build_json
        )
        if platform.system() == "Linux":
            extension = ".so"
        if platform.system() == "Darwin":
            extension = ".dylib"
        if platform.system() == "Windows":
            extension = ".dll"
        prefix = "lib"
    else:
        extension = ".exe"
    return cs_run(
        [
            build_json['cc'],
            "-shared" if build_json[type_name] == "dynamic-lib" else "",
            *get_o_files_existing(),
            "-o",
            join(".", build_folder_name, f"{prefix}{name}{extension}"),
            *ldflags
        ]
    )


def create_static_lib(build_json):
    ldflags = get_ldflags(build_json)
    name = basename(getcwd())
    create_pkg_conf(
        ldflags,
        [f"-I{join(getcwd(), 'include')}"],
        build_json
    )
    if platform.system() == "Linux":
        extension = ".a"
    if platform.system() == "Darwin":
        extension = ".a"
    if platform.system() == "Windows":
        extension = ".lib"
    return cs_run(
        [
            "ar",
            "rcs",
            join(".", build_folder_name, f"lib{name}{extension}"),
            *get_o_files_existing()
        ]
    )


def create_pkg_conf(ldflags, cflags, build_json):
    cwd = getcwd()
    name = basename(cwd)
    with open(join(".", build_folder_name, f"{name}.pc"), "w") as f:
        f.write(f"""
Name: lib{name}
Description: {name} library
Version: {build_json['version']}
Libs: {" ".join(ldflags)}
Cflags: {" ".join(cflags)}
""".replace('\\', '/'))


def get_o_files_existing():
    return [
        file
        for file in get_files_in_dir(join(".", build_folder_name,))
        if file.endswith(".o")
    ]


def compile(build_json):
    ensure_dir_exists(join(".", build_folder_name))
    with Pool() as pool:
        return pool.starmap(
            compile_file_if_modified,
            get_compile_args(build_json)
        )


def get_ldflags(build_json):
    return [
        *build_json.get(ldflags_name, []),
        *get_pkg_config_flags(build_json.get('libs', []), "libs")
    ]


def get_c_flags(build_json):
    return [
        *build_json.get(cflags_name, []),
        *get_pkg_config_flags(build_json.get('libs', []), cflags_name)
    ]


def get_pkg_config_flags(libs, mode):
    return [
        flag
        for lib in libs
        for flag in cs_run([f"pkg-config --{mode} {lib}"]).strip().split(" ")
    ]


def get_o_file_from_c_file(c_file_path):
    return replace_ext(
        replace_path(
            c_file_path,
            join(build_folder_name)
        ),
        "o"
    )


def get_compile_args(build_json):
    return [
        (
            build_json["cc"],
            get_c_flags(build_json),
            c_file_path,
            get_o_file_from_c_file(c_file_path)
        )
        for c_file_path in get_files_in_dir(join(".", src_folder_name))
        if c_file_path.endswith(".c")
    ]


def ensure_dir_exists(dir):
    if not exists(dir):
        makedirs(dir)


def was_c_file_modified(cc, c_flags, c_file_path, o_file_path):
    return max([
        getmtime(c_file_path),
        *[getmtime(key) for key in get_includes(cc, c_flags, c_file_path)]
    ]) > getmtime(o_file_path)


def compile_file_if_modified(cc, c_flags, c_file_path, o_file_path):
    if not exists(o_file_path) or was_c_file_modified(cc, c_flags, c_file_path, o_file_path):
        compile_file(cc, c_flags, c_file_path, o_file_path)


def compile_file(cc, c_flags, c_file_path, o_file_path):
    return cs_run([cc, *c_flags, "-c", c_file_path, "-o", o_file_path])


def get_files_in_dir(dir):
    return [
        join(root, file_path)
        for root, _, file_paths in walk(dir)
        for file_path in file_paths
    ]


def get_includes(cc, c_flags, c_file_path):
    return set([
        abspath(include.lstrip('.').strip())
        for include in cs_run([cc, *c_flags, "-M", "-H", c_file_path]).split('\n')
        if include.startswith(".")
    ])


def replace_path(path, replace):
    return join(replace, basename(path))


def replace_ext(path, replace):
    root, _ = splitext(path)
    return f"{root}.{replace}"


def cs_run(cmd):
    out = run(" ".join(cmd), capture_output=True, text=True)
    if out.returncode != 0:
        raise Exception(out.stderr)
    else:
        return out.stdout


def read_json_file(file):
    with open(file, 'r') as f:
        return loads(f.read())


def parse_args():
    parser = ArgumentParser(description="Ceasium build system.")
    subparsers = parser.add_subparsers(
        dest="command",
        help="Pick a command to run."
    )
    subparsers.add_parser(build_folder_name)
    subparsers.add_parser("run")
    subparsers.add_parser("clean")
    subparsers.add_parser("init")
    install_parser = subparsers.add_parser("install")
    install_parser.add_argument("package_manager")
    args = parser.parse_args()
    return args


def make_path(path):
    return ":".join(["root", *[str(p) for p in path]])


def validate(build_json):
    validate_dict(
        build_json,
        [],
        ["cc", type_name, cflags_name, ldflags_name, "lib-dirs", "libs", "version"],
        ["cc", type_name, "version"],
        lambda x, path: validate_build_json(x, path, build_json)
    )


def validate_build_json(value, path, json):
    if path[-1] == "cc":
        validate_type(value, path, str)
    if path[-1] == type_name:
        validate_type(value, path, str)
        valid_libs = ["exe", "dynamic-lib", "static-lib"]
        if type not in valid_libs:
            raise PathValidationException(
                [type_name, f"must be in {valid_libs}"])
    if path[-1] == cflags_name:
        validate_list_of_flags(value, path)
    if path[-1] == ldflags_name:
        validate_list_of_flags(value, path)
    if path[-1] == "lib-dirs":
        validate_list(
            value,
            path,
            lambda x, path: validate_type(x, path, str)
        )
    if path[-1] == "libs":
        validate_list(
            value,
            path,
            lambda x, path: validate_type(x, path, str)
        )


def validate_list_of_flags(flags, path):
    validate_list(flags, path, validate_flag)


def validate_flag(flag, path):
    validate_type(flag, path, str)
    if not flag.startswith("-"):
        raise PathValidationException(path, "is not a valid flag")


def validate_dict(obj, path, valid_keys, required_keys, validate):
    validate_type(obj, path, dict)
    for key in required_keys:
        if key not in obj:
            raise PathValidationException(path + [key], "is required")
    for key in obj:
        key_path = path + [key]
        if key not in valid_keys:
            raise PathValidationException(key_path, "is not valid")
        validate(obj[key], key_path)


def validate_list(elements, path, validate):
    validate_type(elements, path, list)
    for element in elements:
        validate(element, path + [element])


def validate_type(value, path, target_type):
    if type(value) != target_type:
        raise PathValidationException(
            path,
            f"must be a {target_type.__name__} but is {type(value).__name__}"
        )


def access(json, path):
    value = json
    current_path = []
    for subpath in path:
        validate_type(value, current_path, dict)
        current_path.append(subpath)
        if subpath not in value:
            raise PathValidationException(current_path, "is missing")
        value = value[subpath]
    return value
