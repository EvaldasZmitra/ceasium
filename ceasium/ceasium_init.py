import os

from .ceasium_system_util import ensure_directory_exists, write_if_not_exists


project_build_file_name = "build.json"
build_folder_name = "build"
src_folder_name = "src"
tests_folder_name = "tests"


def init(args):
    src_path = os.path.join(args.path, src_folder_name)
    tests_path = os.path.join(args.path, tests_folder_name)
    ensure_directory_exists(src_path)
    ensure_directory_exists(os.path.join(args.path, build_folder_name))
    ensure_directory_exists(os.path.join(args.path, "include"))
    ensure_directory_exists(os.path.join(args.path, tests_folder_name))
    write_if_not_exists(
        os.path.join(args.path, project_build_file_name),
        """
{
  "name": "myapp",
  "compiler": "gcc",
  "type": "exe",
  "flags": {
    "compiler": ["-g", "-Wall", "-W"],
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

int main()
{
    printf("Hello World!");
    return 0;
}
"""
    )
    write_if_not_exists(
        os.path.join(tests_path, "main.c"),
        """
#include <stdio.h>

int main()
{
    printf("Hello tests!");
    return 0;
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
