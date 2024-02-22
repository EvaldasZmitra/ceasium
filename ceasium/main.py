from multiprocessing import Pool
from json import loads
from subprocess import run
from os.path import abspath, basename, dirname, join, exists, getmtime, splitext
from os import walk, makedirs, getcwd
from os import environ
from argparse import ArgumentParser
from shutil import rmtree
from .constants import colors, pkg_conf_template, get_packages, test_main_path, src_main_path, include_main_path, help_name, package_manager_name, command_help, command_name, missing_name, cmd_install, gitignore_path, lib_name, version_name, os_linux, os_mac, os_windows, key_cc, type_static_lib, pkg_config_name, key_lib_dirs, key_libs, type_dynamic_lib, type_exe, cmd_clean, cmd_init, cmd_run, flags_ld, key_type, include_dir, flags_c, src_dir, build_dir, build_json_path, include_template, build_config_template, main_template, test_template, git_ignore_template
from time import time
import platform


class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class PathValidationException(ValidationException):
    def __init__(self, path, message):
        path = make_path(path)
        super().__init__(f"{path} {message}.")


def main():
    parser = ArgumentParser(description=help_name)
    subparsers = parser.add_subparsers(dest=command_name, help=command_help)
    build_parser = subparsers.add_parser(build_dir)
    run_parser = subparsers.add_parser(cmd_run)
    clean_parser = subparsers.add_parser(cmd_clean)
    init_parser = subparsers.add_parser(cmd_init)
    install_parser = subparsers.add_parser(cmd_install)
    install_parser.add_argument(package_manager_name)

    build_parser.set_defaults(func=build_cmd)
    run_parser.set_defaults(func=run_cmd)
    clean_parser.set_defaults(func=clean_cmd)
    init_parser.set_defaults(func=init_cmd)
    install_parser.set_defaults(func=install_cmd)

    args = parser.parse_args()
    args.func(args)


def clean_cmd(args):
    print(f"Removing path {build_dir}")
    rmtree(build_dir, True)


def run_cmd(args):
    path = join(build_dir, get_name())
    cs_run([path])


def init_cmd(args):
    safe_write(build_json_path, build_config_template)
    safe_write(src_main_path, main_template)
    safe_write(test_main_path, test_template)
    safe_write(gitignore_path, git_ignore_template)
    safe_write(include_main_path, include_template)


def install_cmd(args):
    build_json = read_json_file(build_json_path)
    packages = get_packages()
    for lib in build_json.get(key_libs, []):
        cs_get_output(packages[lib][args.package_manager])


def build_cmd(args):
    build_json = read_json_file(build_json_path)
    environ[pkg_config_name] = ";".join([
        environ.get(pkg_config_name, ""),
        *[abspath(dir) for dir in build_json.get(key_lib_dirs, [])]
    ])
    compile_results = compile(build_json)
    for compile_result in compile_results:
        if compile_result["modified"]:
            pass
        else:
            print_grey(f"Unchanged: {compile_result['file']}")
    {
        type_exe: link_exe,
        type_dynamic_lib: link_dynamic_lib,
        type_static_lib: create_static_lib
    }[build_json[key_type]](build_json)
    return {
        "compile_result": compile_results
    }


def link_exe(build_json):
    extension = {
        os_linux: "",
        os_mac: "",
        os_windows: "exe"
    }[platform.system()]
    return cs_get_output(
        [
            build_json[key_cc],
            *get_o_files_existing(),
            "-o",
            join(build_dir, replace_ext(get_name(), extension)),
            *[
                *build_json.get(flags_ld, []),
                *get_pkg_config_flags(build_json.get(key_libs, []), key_libs)
            ]
        ]
    )


def link_dynamic_lib(build_json):
    extension = {
        os_linux: "so",
        os_mac: "dynlib",
        os_windows: "dll"
    }[platform.system()]
    create_pkg_conf(
        [
            *build_json.get(flags_ld, []),
            *[
                *get_pkg_config_flags(build_json.get(key_libs, []), key_libs),
                f"-L{abspath(join(getcwd(), build_dir))}"
            ]
        ],
        [f"-I{join(getcwd(), include_dir)}"],
        build_json['version']
    )
    return cs_get_output(
        [
            build_json[key_cc],
            "-shared",
            *get_o_files_existing(),
            "-o",
            join(build_dir, replace_ext(get_name(), extension)),
            *[
                *build_json.get(flags_ld, []),
                *get_pkg_config_flags(build_json.get(key_libs, []), key_libs)
            ]
        ]
    )


def compile(build_json):
    ensure_dir_exists(join(build_dir))
    with Pool() as pool:
        return pool.starmap(
            compile_file_if_modified,
            get_compile_args(
                build_json[key_cc],
                build_json.get(flags_c, []),
                build_json.get(key_libs, [])
            )
        )


def create_static_lib(build_json):
    create_pkg_conf(
        [
            *build_json.get(flags_ld, []),
            *get_pkg_config_flags(build_json.get(key_libs, []), key_libs)
        ],
        [f"-I{join(getcwd(), include_dir)}"],
        build_json['version']
    )
    package_static_lib(
        join(
            build_dir,
            f"{lib_name}{get_name()}{get_lib_extension()}"
        ),
        *get_o_files_existing()
    )


def get_compile_args(cc, cflags, libs):
    return [
        (cc, get_c_flags(cflags, libs), c_file_path, c_to_o_file(c_file_path))
        for c_file_path in get_files_in_dir(join(src_dir))
        if c_file_path.endswith(".c")
    ]


def get_c_flags(cflags, libs):
    return [*cflags, *get_pkg_config_flags(libs, flags_c)]


def get_includes(cc, c_flags, c_file_path):
    return set([
        abspath(include.lstrip('.').strip())
        for include in cs_get_output([cc, *c_flags, "-M", "-H", c_file_path]).split('\n')
        if include.startswith(".")
    ])


def get_lib_extension():
    if platform.system() == os_linux:
        extension = ".a"
    if platform.system() == os_mac:
        extension = ".a"
    if platform.system() == os_windows:
        extension = f".{lib_name}"
    return extension


def get_name():
    return basename(getcwd())


def create_pkg_conf(ldflags, cflags, version):
    name = get_name()
    pc_name = replace_ext(name, "pc")
    pc_path = join(build_dir, pc_name)
    with open(pc_path, "w") as f:
        f.write(
            pkg_conf_template(
                name,
                version,
                " ".join(cflags),
                " ".join(ldflags)
            ).replace('\\', '/')
        )


def get_o_files_existing():
    return [
        file for file in get_files_in_dir(build_dir)
        if file.endswith(".o")
    ]


def c_to_o_file(c_file_path):
    return replace_ext(replace_path(c_file_path, join(build_dir)), "o")


def ensure_dir_exists(dir):
    if not exists(dir) and dir != '':
        makedirs(dir)


def was_c_file_modified(cc, c_flags, c_file_path, o_file_path):
    return get_c_file_code_mod_time(cc, c_flags, c_file_path) > getmtime(o_file_path)


def get_c_file_code_mod_time(cc, c_flags, c_file_path):
    return max([
        getmtime(c_file_path),
        *[getmtime(key) for key in get_includes(cc, c_flags, c_file_path)]
    ])


def compile_file_if_modified(cc, c_flags, c_file_path, o_file_path):
    start = time()
    if not exists(o_file_path) or was_c_file_modified(cc, c_flags, c_file_path, o_file_path):
        compile_file(cc, c_flags, c_file_path, o_file_path)
        return {
            "file": c_file_path,
            "modified": True,
            "duration": time() - start
        }
    else:
        return {
            "file": c_file_path,
            "modified": False,
            "duration": time() - start
        }


def get_files_in_dir(dir):
    return [
        join(root, file_path)
        for root, _, file_paths in walk(dir)
        for file_path in file_paths
    ]


def replace_path(path, replace):
    return join(replace, basename(path))


def replace_ext(path, replace):
    root, _ = splitext(path)
    if replace != "":
        return f"{root}.{replace.lstrip('.')}"
    else:
        return root


def safe_write(file, text):
    ensure_dir_exists(dirname(file))
    with open(file, "w") as f:
        f.write(text)


def read_json_file(file):
    with open(file, 'r') as f:
        return loads(f.read())


def make_path(path):
    return ":".join([str(p) for p in path])


def get_pkg_config_flags(libs, mode):
    return [
        flag
        for lib in libs
        for flag in cs_get_output([f"pkg-config --{mode} {lib}"]).strip().split(" ")
    ]


def package_static_lib(output_path, o_files):
    return cs_get_output(["ar", "rcs", output_path, o_files])


def compile_file(cc, c_flags, c_file_path, o_file_path):
    return cs_get_output([cc, *c_flags, "-c", c_file_path, "-o", o_file_path])


def cs_get_output(cmd):
    out = run(" ".join(cmd), capture_output=True, text=True)
    if out.returncode != 0:
        raise Exception(out.stderr)
    else:
        return out.stdout


def cs_run(cmd):
    out = run(" ".join(cmd), capture_output=True, text=True)
    if out.returncode != 0:
        raise Exception(out.stderr)
    else:
        return out.stdout


def validate(build_json):
    validate_dict(
        build_json,
        [],
        [key_cc, key_type, flags_c, flags_ld,
            key_lib_dirs, key_libs, version_name],
        [key_cc, key_type, version_name],
        lambda x, path: validate_build_json(x, path)
    )


def validate_build_json(value, path):
    if path[-1] == key_cc:
        validate_type(value, path, str)
    if path[-1] == key_type:
        validate_build_type(value, path)
    if path[-1] == flags_c:
        validate_list_of_flags(value, path)
    if path[-1] == flags_ld:
        validate_list_of_flags(value, path)
    if path[-1] == key_lib_dirs:
        validate_list(value, path, lambda x, path: validate_type(x, path, str))
    if path[-1] == key_libs:
        validate_list(value, path, lambda x, path: validate_type(x, path, str))


def validate_build_type(value, path):
    validate_type(value, path, str)
    valid_libs = [type_exe, type_dynamic_lib, type_static_lib]
    if value not in valid_libs:
        raise PathValidationException([key_type], f"must be in {valid_libs}")


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
            raise PathValidationException(current_path, missing_name)
        value = value[subpath]
    return value


def print_red(text):
    print(f"{colors.RED}{text}{colors.RESET}")


def print_green(text):
    print(f"{colors.GREEN}{text}{colors.RESET}")


def print_grey(text):
    print(f"{colors.DARK_GREY}{text}{colors.RESET}")


def print_yellow(text):
    print(f"{colors.YELLOW}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
