import os
import argparse
import json
import os
from .constants import help_template, project_build_file_name


def configure_arg_parser():
    parser = argparse.ArgumentParser(description="Builds a C project.")
    subparsers = parser.add_subparsers(
        dest='command',
        help="Available commands"
    )
    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--path", default=os.getcwd())
    install_parser = subparsers.add_parser('install', help='Installs packages')
    install_parser.add_argument(
        'package_manager',
        help=help_template
    )
    install_parser.add_argument("--path", default=os.getcwd())
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--path", default=os.getcwd())
    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--path", default=os.getcwd())
    vs_code_parser = subparsers.add_parser("vscode")
    vs_code_parser.add_argument("--path", default=os.getcwd())
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--path", default=os.getcwd())
    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--path", default=os.getcwd())
    return parser


def parse_arguments():
    parser = configure_arg_parser()
    return parser.parse_args()


def read_config(file_path):
    build_file_path = os.path.join(file_path, project_build_file_name)
    with open(build_file_path, "r") as file:
        return json.load(file)
