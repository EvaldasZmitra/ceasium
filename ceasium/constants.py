from os.path import join

build_dir = "build"
src_dir = "src"
tests_dir = "tests"
include_dir = "include"

main_c_file_name = "main.c"
main_h_file_name = "main.h"
gitignore_path = ".gitignore"
build_json_path = "build.json"

flags_c = "cflags"
flags_ld = "ldflags"

os_linux = "Linux"
os_mac = "Darwin"
os_windows = "Windows"

type_dynamic_lib = "dynamic-lib"
type_static_lib = "static-lib"
type_exe = "exe"

dyn_lib_name_linux = "so"
dyn_lib_name_windows = "dll"
dyn_lib_name_mac = "dylib"

cmd_install = "install"
cmd_init = "init"
cmd_clean = "clean"
cmd_run = "run"

key_cc = "cc"
key_type = "type"
key_libs = "libs"
key_lib_dirs = "lib-dirs"

lib_name = "lib"
version_name = "version"
pkg_config_name = "PKG_CONFIG_PATH"

command_name = "command"
missing_name = "is missing"
command_help = "Pick a command to run."
package_manager_name = "package_manager"
help_name = "Ceasium build system."

src_main_path = join(src_dir, main_c_file_name)
test_main_path = join(tests_dir, main_c_file_name)
include_main_path = join(include_dir, main_h_file_name)


def get_packages():
    with open("./packages.json", "r") as f:
        return f.read()


colors_arr = [
    '\033[0m',
    '\033[91m',
    '\033[92m',
    '\033[93m',
    '\033[94m',
    '\033[95m',
    '\033[96m',
    '\033[97m',
    '\033[1m',
    '\033[4m',
    '\033[37m',
    '\033[90m'
]


class colors:
    RESET = colors_arr[0]
    RED = colors_arr[1]
    GREEN = colors_arr[2]
    YELLOW = colors_arr[3]
    BLUE = colors_arr[4]
    MAGENTA = colors_arr[5]
    CYAN = colors_arr[6]
    WHITE = colors_arr[7]
    BOLD = colors_arr[8]
    UNDERLINE = colors_arr[9]
    LIGHT_GREY = colors_arr[10]
    DARK_GREY = colors_arr[11]


include_template = """
#ifndef MAIN_H
#define MAIN_H



#endif
"""

build_config_template = """{
  "cc": "gcc",
  "version": "0.0.0",
  "type": "exe",
  "cflags": [
    "-I./include",
    "-g",
    "-W",
    "-Wall",
    "-O3",
    "-fopenmp",
    "-fdiagnostics-color=always"
  ],
  "ldflags": ["-lopengl32", "-fopenmp"],
  "lib-dirs": [],
  "libs": []
}
"""

main_template = """#include <stdio.h>
#include <main.h>

int main()
{
    printf("Hello World!");
    return 0;
}
"""

test_template = """#include <stdio.h>

int main()
{
    printf("Hello tests!");
    return 0;
}
"""

git_ignore_template = """build
"""


def pkg_conf_template(name, version, cflags, ldflags):
    return f"""Name: lib{name}
Description: {name} library
Version: {version}
Libs: {ldflags}
Cflags: {cflags}
"""
