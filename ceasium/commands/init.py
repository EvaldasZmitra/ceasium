import os
from ..shell import write_if_not_exists
from ..system_util import ensure_directory_exists
from ..constants import build_config_template, main_template, test_template, git_ignore_template, src_folder_name, tests_folder_name, build_folder_name, project_build_file_name


def init(args):
    src_path = os.path.join(args.path, src_folder_name)
    tests_path = os.path.join(args.path, tests_folder_name)
    ensure_directory_exists(src_path)
    ensure_directory_exists(os.path.join(args.path, build_folder_name))
    ensure_directory_exists(os.path.join(args.path, "include"))
    ensure_directory_exists(os.path.join(args.path, tests_folder_name))
    write_if_not_exists(
        os.path.join(args.path, project_build_file_name),
        build_config_template
    )
    write_if_not_exists(os.path.join(src_path, "main.c"), main_template)
    write_if_not_exists(os.path.join(tests_path, "main.c"), test_template)
    write_if_not_exists(os.path.join(
        args.path, ".gitignore"), git_ignore_template)
