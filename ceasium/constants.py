build_folder_name = "build"
project_build_file_name = "build.json"
src_folder_name = "src"
tests_folder_name = "tests"
o_folder_name = "o"
cflags_name = "cflags"
include_name = "include"
type_name = "type"
ldflags_name = "ldflags"

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

build_config_template = """
{
  "name": "app",
  "objs": {
    "src": {
      "cc": "gcc",
      "cflags": [
        "-I./include",
        "-g",
        "-W",
        "-Wall",
        "-O3",
        "-fdiagnostics-color=always"
      ]
    },
    "test": {
      "cc": "gcc",
      "cflags": [
        "-I./include",
        "-g",
        "-W",
        "-Wall",
        "-O3",
        "-fdiagnostics-color=always"
      ]
    }
  },
  "outs": {
    "exe": {
      "src": {
        "cc": "gcc",
        "objs": ["src"]
      },
      "test": {
        "cc": "gcc",
        "objs": ["src", "test"]
      }
    }
  }
}
"""

main_template = """
#include <stdio.h>
#include <main.h>

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

packages = {
    "glew": {
        "apt": "apt install glew",
        "msys2": ["pacman",  "-S", "--needed", "--noconfirm", "mingw-w64-x86_64-glew"]
    },
    "sdl2": {
        "apt": "apt install sdl2",
        "msys2": ["pacman",  "-S", "--needed", "--noconfirm", "mingw-w64-x86_64-SDL2"]
    },
    "glib-2.0": {
        "apt": "apt install glib",
        "msys2": ["pacman",  "-S", "--needed", "--noconfirm", "mingw-w64-x86_64-glib2"]
    },
    "assimp": {
        "apt": "apt install assimp",
        "msys2": ["pacman",  "-S", "--needed", "--noconfirm", "mingw-w64-x86_64-assimp"]
    }
}
