from json import loads
from os.path import join, exists, basename, getmtime
from os import walk
from argparse import ArgumentParser
from subprocess import check_output
from pkgconfig import cflags


def main():
    build_json = read_json_file("./build.json")
    validate_build_json(build_json)
    parser = ArgumentParser(description="Ceasium build system.")
    subparsers = parser.add_subparsers(
        dest="command",
        help="Pick a command to run."
    )
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument(
        "subcommand",
        help="Name of the build."
    )
    args = parser.parse_args()
    if args.command == "build":
        run_build(build_json, args)


def run_build(build_json, args):
    validate_build_json_for_build(build_json, args.subcommand)
    run_build_subcommand(build_json, args.subcommand)


def run_build_subcommand(build_json, subcommand):
    build = build_json["build"][subcommand]
    validate_build_json_subcommand(build)
    for compile in build.get('compile', []):
        run_build_json_compile(subcommand, build_json)


def run_build_json_compile(name, build, build_json):
    validate_build_compile(name, build, build_json)
    # if 'compile' in build_json:
    #     compiles = build_json["compile"]
    #     c_flags = get_c_flags(build_json, "compile")
    #     libs = build_json.get("libs", {})
    #     if "compile" in build:
    #         for compile_name in build['compile']:
    #             if compile_name in compiles:
    #                 c_flags = []
    #                 run_build_compile(
    #                     compile_name,
    #                     build_json.get("cc"),
    #                     compiles[compile_name],
    #                     c_flags,
    #                     libs
    #                 )
    #             else:
    #                 msg = f"Unknown compile target '{compile_name}'. Available {list(compiles.keys())}."
    #                 raise Exception(msg)
    #     else:
    #         raise Exception(
    #             f"Missing section in build.json. Ensure build:{args.subcommand}:compile exists")
    # else:
    #     raise Exception(
    #         f"Missing section in build.json. Ensure build:compile exists"
    #     )


def validate_build_compile(name, compiles, build_json):
    if type(compiles) != list:
        raise Exception(f"build:{name}:compile must be an array.")
    for compile_name in compiles:
        if type(compile_name) != str:
            raise Exception(
                f"build:{name}:compile:{compile_name} must be a string."
            )
        if compile_name not in build_json['compile']:
            raise Exception(
                f"build:{name}:compile:{compile_name} was not in {list(build_json['compile'].keys())}"
            )

def validate_build_json_subcommand(build):
    valid_keys = set(['compile', 'link'])
    for key in build:
        if key not in valid_keys:

def validate_build_json_for_build(build, subcommand):
    if "build" not in build:
        raise Exception("Missing 'build' section.")
    if subcommand not in build['build']:
        raise Exception(f"Missing build:{subcommand}.")


def validate_build_json(build):
    valid_keys = set(["libs", "cflags", "cc", "compile", "link", "build"])
    for key in build:
        if key not in valid_keys:
            raise Exception(f"{key} is not a valid key.")


def run_build_compile(name, cc, compile_json, c_flags, libs):
    if 'dirs' in compile_json:
        for dir in compile_json['dirs']:
            if not exists(dir):
                raise Exception(f"Path {dir} does not exist.")
        c_file_paths = [
            join(root, file)
            for dir in compile_json['dirs']
            for root, _, files in walk(dir)
            for file in files
            if file.endswith('.c')
        ]
        if len(c_file_paths) > 0:
            o_file_paths = [
                join('.', 'build', name, f"{basename(path)[:-2]}.o")
                for path in c_file_paths
            ]
            cc_override = compile_json.get("cc")
            if cc == None and cc_override == None:
                raise Exception(
                    f"Missing section in build.json, 'cc' not specified for compile:{name}."
                )
            if cc_override != None:
                cc = cc_override
            cmds = []
            if "libs" in compile_json:
                if type(compile_json["libs"]) == list:
                    true_c_flags = {}
                    for lib in compile_json["libs"]:
                        if lib in libs:
                            if type(lib) == str:
                                true_c_flags[lib] = libs[lib]
                            else:
                                raise Exception(
                                    f"compile:{name}:libs:{lib} is not a string."
                                )
                        else:
                            raise Exception(
                                f"compile:{name}:libs:{lib} is not in {list(libs.keys())}"
                            )
                else:
                    raise Exception(
                        f"compile:{name}:libs must be an array."
                    )
            if "cflags" in compile_json:
                if type(compile_json["cflags"]) != list:
                    raise Exception(
                        f"cflags must be a list in compile:{name}."
                    )
                c_flags = [
                    *c_flags,
                    *get_c_flags(compile_json, f"compile:{name}")
                ]
            for (src_path, o_path) in zip(c_file_paths, o_file_paths):
                src_mod_time = get_src_mod_time(src_path, cc)
                o_mod_time = get_o_mod_time(o_path)
                # if src_mod_time > o_mod_time:
                #     c_flags_str = get_c_flags_string(c_flags, libs)
                #     cmds.append(
                #         f"{cc} {c_flags_str} -c {src_path} -o {o_path}"
                #     )
        else:
            raise Exception(f"No .c files exist under {dir}")
    else:
        msg = f"Missing section in build.json. Ensure compile:{name}:dirs exits."
        raise Exception(msg)


def get_c_flags(json, path):
    c_flags = []
    if "cflags" in json:
        if type(json["cflags"]) != list:
            raise Exception(
                f"{path}:cflags must be a list."
            )
    for cflag in json["cflags"]:
        if type(cflag) != str:
            raise Exception(f"In {path}:cflags cflag must be a string.")
        if not cflag.startswith("-"):
            raise Exception(f"In {path}:cflags cflag must start with '-'.")
        c_flags.append(cflag)
    return c_flags


def get_c_flags_string(c_flags, libraries):
    c_flags_all = [f'-I{join(".", "include")}']
    for library in libraries:
        try:
            c_flags_all += cflags(library).split(" ")
        except Exception as e:
            pass
    return " ".join(set(c_flags_all + c_flags))


def get_o_mod_time(path):
    if exists(path):
        return getmtime(path)
    return 0


def get_src_mod_time(path, cc):
    h_paths = get_included_files(path, cc)
    mod_times = [getmtime(path) for path in h_paths]
    mod_times.append(getmtime(path))
    return max(mod_times)


def get_included_files(src_file_path, cc):
    h_paths = []
    compiler_flags_cmd = [cc, "-MM", src_file_path]
    cmd_result = check_output(
        compiler_flags_cmd,
        universal_newlines=True
    )
    cmd_result_lines = cmd_result.splitlines()[1:]
    for s in cmd_result_lines:
        sanitized_path = remove_trailing_backslash(s).strip()
        h_paths.append(sanitized_path)
    return h_paths


def remove_trailing_backslash(input_string):
    if input_string.endswith("\\"):
        return input_string[:-1]
    else:
        return input_string


def read_json_file(file):
    with open(file, 'r') as f:
        return loads(f.read())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
