from multiprocessing import Pool
from json import loads
from subprocess import run
from os.path import abspath, basename, join, exists, getmtime, splitext
from os import walk, makedirs
from argparse import ArgumentParser
from shutil import rmtree


class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class PathValidationException(ValidationException):
    def __init__(self, path, message):
        path = make_path(path)
        super().__init__(f"{path} {message}.")


def main():
    args = parse_args()
    if args.command == "build":
        build(args.build_type, args.build_key)
    if args.command == "run":
        build_json = read_json_file("./build.json")
        cs_run(join(".", "build", build_json["name"]))
    if args.command == "init":
        pass
    if args.command == "install":
        pass
    if args.command == "clean":
        rmtree(join(".", "build"))
    if args.command == "add":
        pass


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)


def build(build_type, build_key):
    build_json = read_json_file("./build.json")
    validate(build_json)
    compile(build_type, build_key, build_json)
    if build_type == "exe" or build_type == "dynamic-lib":
        link(build_type, build_key, build_json)
    if build_type == "static-lib":
        create_static_lib()


def link_dll(build_type, build_key, build_json):
    return cs_run(
        [
            build_json["outs"][build_type][build_key]['cc'],
            "-static",
            *get_o_files(build_type, build_key, build_json),
            "-o",
            join(".", "build", build_json["name"]),
            *get_ldflags(build_json, build_type, build_key)
        ]
    )


def create_static_lib(build_type, build_key, build_json):
    return cs_run(
        " ".join(
            [
                "ar",
                "rcs",
                build_json["name"],
                *get_o_files(build_type, build_key, build_json)
            ]
        )
    )


def link(build_type, build_key, build_json):
    return cs_run(
        " ".join(
            [
                build_json["outs"][build_type][build_key]['cc'],
                "-shared" if build_type == "dynamic-lib" else "",
                *get_o_files(build_type, build_key, build_json),
                "-o",
                join(".", "build", build_json["name"]),
                *get_ldflags(build_json, build_type, build_key)
            ]
        )
    )


def get_ldflags(build_json, build_type, build_key):
    return [
        *build_json["outs"][build_type][build_key]["ldflags"],
        *get_pkg_config_flags(
            get_libs(build_type, build_key, build_json),
            "libs"
        )
    ]


def get_libs(build_type, build_key, build_json):
    return [
        {
            "name": build_json["libs"][lib]["name"],
            "version": build_json["libs"][lib]["version"]
        }
        for obj in build_json["outs"][build_type][build_key]["objs"]
        for lib in build_json["objs"][obj]["libs"]
    ]


def get_o_files(build_type, build_key, build_json):
    return [
        file
        for obj in build_json["outs"][build_type][build_key]["objs"]
        for file in get_files_in_dir(join(".", "build", obj), "o")
    ]


def compile(build_type, build_key, build_json):
    create_build_dirs(build_type, build_key, build_json)
    with Pool() as pool:
        return pool.starmap(
            compile_file,
            get_compile_args(build_type, build_key, build_json)
        )


def get_compile_args(build_type, build_key, build_json):
    return [
        (
            build_json["objs"][obj_key]["cc"],
            get_cflags(build_json, obj_key),
            get_o_files(c_file_path, obj_key),
            c_file_path
        )
        for obj_key in build_json["outs"][build_type][build_key]["objs"]
        for c_file_path in get_files_in_dir(join(".", obj_key), ".c")
    ]


def create_build_dirs(build_type, build_key, build_json):
    for obj_key in build_json["outs"][build_type][build_key]["objs"]:
        o_dir = join(".", "build", obj_key)
        if not exists(o_dir):
            makedirs(o_dir)


def get_o_files(c_file_path, obj_key):
    return replace_ext(
        replace_path(
            c_file_path,
            join("build", obj_key)
        ),
        "o"
    )


def get_cflags(build_json, obj_key):
    return [
        *build_json["objs"][obj_key]["cflags"],
        *get_pkg_config_flags(
            [
                build_json["libs"][lib]
                for lib in build_json["objs"][obj_key]['libs']
            ],
            "cflags"
        )
    ]


def was_modified(cc, c_flags, o_file_path, c_file_path):
    return max([
        getmtime(c_file_path),
        *[getmtime(key) for key in get_includes(c_file_path, c_flags, cc)]
    ]) > getmtime(o_file_path)


def compile_file(cc, c_flags, o_file_path, c_file_path):
    if not exists(o_file_path) or was_modified(cc, c_flags, o_file_path, c_file_path):
        return cs_run(
            " ".join([cc, *c_flags, "-c", c_file_path, "-o", o_file_path])
        )


def get_pkg_config_flags(libs, mode):
    return [
        flag
        for lib in libs
        for flag in cs_run(
            f"pkg-config --{mode} \"{lib['name']} >= {lib['version']}\""
        ).strip().split(" ")
    ]


def get_files_in_dir(dir, ext):
    return [
        join(root, file_path)
        for root, _, file_paths in walk(dir)
        for file_path in file_paths
        if file_path.endswith(ext)
    ]


def get_includes(src_path, c_flags, cc):
    return set([
        abspath(include.lstrip('.').strip())
        for include in cs_run([cc, *c_flags, "-M", "-H", src_path]).split('\n')
        if include.startswith(".")
    ])


def replace_path(path, replace):
    return join(replace, basename(path))


def replace_ext(path, replace):
    root, _ = splitext(path)
    return f"{root}.{replace}"


def cs_run(cmd):
    out = run(cmd, capture_output=True, text=True)
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
    subparsers.add_parser("run")
    args = parser.parse_args()
    return args


def make_path(path):
    path = [str(p) for p in path]
    return ":".join(["root", *path])


def validate(build_json):
    validate_dict(
        build_json,
        [],
        ["name", "libs", "objs", "outs"],
        ["name", "outs"],
        lambda x, path: True
    )
    validate_type(build_json["name"], ["name"], str)
    libs = build_json.get("libs", {})
    for lib in libs:
        validate_dict(
            libs[lib],
            ["libs", lib],
            ["name", "version"],
            ["name", "version"],
            lambda x, path: validate_type(x, path, str)
        )
    for obj in build_json.get("objs", {}):
        validate_dict(
            build_json["objs"][obj],
            ["objs", obj],
            ["cc", "cflags", "libs"],
            ["cc"],
            lambda x, path: validate_obj(x, path, build_json)
        )


def validate_libs(value, path):
    validate_dict(
        value,
        path,
        ["name", "version"],
        ["name", "version"],
        lambda x, p: validate_type(x, p, str)
    )


def validate_compile_link_all(json, path):
    obj = access(json, path)
    validate_type(obj, path, dict)
    for key in obj:
        validate_dict(
            obj[key],
            path + [key],
            ["cflags", "dirs", "ldflags", "libs", "cc"],
            ["dirs"],
            lambda value, path: validate_obj(value, path, json)
        )


def validate_obj(value, path, json):
    if path[-1] in ["libs", "dirs"]:
        validate_list(value, path, lambda x, path: validate_type(x, path, str))
    if path[-1] in ["cflags", "ldflags"]:
        validate_list_of_flags(value, path)
    if path[-1] == "libs":
        libs = access(json, ["libs"])
        validate_dict(
            libs,
            ["libs"],
            libs.keys(),
            value,
            lambda a, b: True
        )
    if path[-1] == "cc":
        validate_type(access(json, path), path, str)


def validate_build(value, path, json):
    if len(path) == 3:
        validate_list(
            value,
            path,
            lambda x, path:
                validate_type(x, path, str) and
                access(json, [path[-1], x])
        )


def validate_at_least_one(json, paths):
    for path in paths:
        try:
            access(json, path)
            return
        except PathValidationException:
            pass
    paths_str = [make_path(path) for path in paths]
    raise ValidationException(f"At least one in {paths_str} must exist.")


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


def validate_not_empty(elements, path):
    if len(elements) == 0:
        raise PathValidationException(path, "cannot be empty")


def validate_list(elements, path, validate):
    validate_type(elements, path, list)
    for element in elements:
        validate(element, path + [element])


def validate_type(value, path, target_type):
    if type(value) != target_type:
        raise PathValidationException(
            path, f"must be a {target_type.__name__} but is {
                type(value).__name__}"
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
