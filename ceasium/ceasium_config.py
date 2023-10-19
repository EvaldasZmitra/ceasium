import os
import argparse
import json
import os
import platform


project_build_file_name = "build.json"


def configure_arg_parser():
    os_name = platform.system()
    parser = argparse.ArgumentParser(
        description="Builds a C project.")
    parser.add_argument(
        'action',
        choices=["init", "build", "install", "run", "clean"],
        type=str
    )
    parser.add_argument(
        "--path",
        type=str,
        help="The root path of the project.",
        default=os.getcwd(),
        required=False)
    parser.add_argument(
        "--package-env",
        type=str,
        help="""
        Package environment defaults to os name [Windows, Linux, Darwin].
        A value can be passed to use different install commands defined in
        build.json. For example - define new env Snap, pass in value Snap and it
        will use snap commands from build.json to install packages.""",
        default=os_name,
        required=False)
    return parser


def parse_arguments():
    parser = configure_arg_parser()
    return parser.parse_args()


def read_config(file_path):
    build_file_path = os.path.join(file_path, project_build_file_name)
    with open(build_file_path, "r") as file:
        return json.load(file)
