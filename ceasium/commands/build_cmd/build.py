from .get_flags import gen_pkg_config_cc_flags, gen_pkg_config_linker_flags
from .compile import compile
from ...shell import print_blue, print_green, print_grey, print_yellow
from ...config import read_config
from ...system_util import get_output, run_timed
from ...constants import build_folder_name
from os.path import join


def build(args):
    print_blue("Building...")
    build_config = read_config(args.path)
    if build_config['static']:
        build_static(args.path, build_config)
    else:
        build_linked(args.path, build_config)


def build_linked(root_path, build_config):
    libraries = build_config['libraries']
    compiler_flags = build_config['flags']['compiler']
    compiler = build_config['compiler']
    compile_results = compile(root_path, libraries, compiler_flags, compiler)
    output_path = join(root_path, build_folder_name, build_config['name'])
    linker_command = [
        compiler,
        *compiler_flags,
        *gen_pkg_config_cc_flags(libraries),
        *[result["o_file"] for result in compile_results],
        "-o",
        output_path,
        *build_config['flags']['linker'],
        *gen_pkg_config_linker_flags(libraries)
    ]
    linker_output = run_timed(linker_command)
    print_compile_result(compile_results)
    if linker_output['result']:
        print_yellow(
            f"Linked {output_path} in {round(linker_output['time'], 2)}s."
        )
        print(linker_output['result'])
    else:
        print_green(
            f"Linked {output_path} in {round(linker_output['time'], 2)}s."
        )


def build_static(root_path, build_config):
    libraries = build_config['libraries']
    compiler = build_config['compiler']
    output_path = join(root_path, build_folder_name, build_config['name'])
    compile_results = compile(
        root_path,
        libraries,
        build_config['flags']['compiler'],
        compiler
    )
    archive_command = [
        "ar",
        "rcs",
        output_path,
        *[result["o_file"] for result in compile_results]
    ]
    print_compile_result(compile_results)
    get_output(archive_command)
    print_green(f"Created shared library {output_path}.")


def print_compile_result(compile_results):
    for compile_result in compile_results:
        if compile_result["was_built"]:
            t = round(compile_result['time'], 2)
            if compile_result['result']:
                print_yellow(f"Built {compile_result['c_file']} in {t}s.")
                print(compile_result['result'])
            else:
                print_green(f"Built {compile_result['c_file']} in {t}s.")
        else:
            print_grey(f"Unchanged {compile_result['c_file']}")
