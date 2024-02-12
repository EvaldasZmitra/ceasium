build_folder_name = "build"
project_build_file_name = "build.json"
build_folder_name = "build"
src_folder_name = "src"
tests_folder_name = "tests"
o_folder_name = "o"

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


build_config_template = """
{
  "name": "myapp",
  "compiler": "gcc",
  "type": "exe",
  "flags": {
    "compiler": [
      "-g", 
      "-Wall", 
      "-W",
      "-O3",
      "-fdiagnostics-color=always"
    ],
    "linker": []
  },
  "libraries": [],
  "packages": {
    "pacman": [],
    "apt": []
  }
}
"""

main_template = """
#include <stdio.h>

int main()
{
    printf("Hello World!");
    return 0;
}
"""

test_template = """
#include <stdio.h>

int main()
{
    printf("Hello tests!");
    return 0;
}
"""

git_ignore_template = """
build
"""

help_template = """
Package environment defaults to os name [Windows, Linux, Darwin].
A value can be passed to use different install commands defined in
build.json. For example - define new env Snap, pass in value Snap and it
will use snap commands from build.json to install packages.
"""
