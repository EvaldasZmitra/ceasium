import os
import argparse
import json
import os


project_build_file_name = "build.json"


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
        help="""
        Package environment defaults to os name [Windows, Linux, Darwin].
        A value can be passed to use different install commands defined in
        build.json. For example - define new env Snap, pass in value Snap and it
        will use snap commands from build.json to install packages."""
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
