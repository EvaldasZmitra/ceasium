import os

from .ceasium_system_util import ensure_directory_exists, write_if_not_exists


project_build_file_name = "build.json"
build_folder_name = "build"
src_folder_name = "src"


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
  "flags": {
    "compiler": ["-g", "-Wall", "-Werror"],
    "linker": []
  },
  "libraries": [],
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
    write_if_not_exists(
        os.path.join(src_path, ".gitignore"),
        """
build
.vscode
"""
    )
