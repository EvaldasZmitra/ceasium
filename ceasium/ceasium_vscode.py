import os
import subprocess
import pkgconfig
import json

from .ceasium_system_util import ensure_directory_exists, write_if_not_exists
from .ceasium_config import read_config

vscode_folder_name = ".vscode"
include_folder_name = "include"
c_cpp_properties_file_name = "c_cpp_properties.json"
launch_file_name = "launch.json"


def vscode(args):
    vscode_path = os.path.join(args.path, vscode_folder_name)
    ensure_directory_exists(vscode_path)
    c_cpp_file = os.path.join(vscode_path, c_cpp_properties_file_name)
    launch_file = os.path.join(vscode_path, launch_file_name)
    build_config = read_config(args.path)
    libraries = build_config['libraries']
    c_cpp_properties_json = gen_c_cpp_properties_json(libraries, args.path)
    launch_json = gen_launch_json(build_config["name"])
    write_if_not_exists(
        c_cpp_file,
        c_cpp_properties_json
    )
    write_if_not_exists(
        launch_file,
        launch_json
    )


def gen_launch_json(name):
    launch_json = {
        "configurations": [
            {
                "name": "C/C++: g++.exe build and debug active file",
                "type": "cppdbg",
                "request": "launch",
                "program": f"${{workspaceRoot}}\\build\\{name}.exe",
                "args": [],
                "stopAtEntry": False,
                "cwd": "${workspaceRoot}",
                "environment": [],
                "externalConsole": False,
                "MIMode": "gdb",
                "miDebuggerPath": subprocess.getoutput("where gdb"),
                "setupCommands": [
                    {
                        "description": "Enable pretty-printing for gdb",
                        "text": "-enable-pretty-printing",
                        "ignoreFailures": True
                    },
                    {
                        "description": "Set Disassembly Flavor to Intel",
                        "text": "-gdb-set disassembly-flavor intel",
                        "ignoreFailures": True
                    }
                ]
            }
        ],
        "version": "2.0.0"
    }
    return json.dumps(launch_json, indent=4)


def gen_c_cpp_properties_json(libraries, path):
    include_paths = get_include_paths(libraries)
    include_paths.append(
        os.path.join(path, include_folder_name)
    )
    c_cpp_json = {
        "configurations": [
            {
                "name": "Wind32",
                "includePath": include_paths,
                "defines": [
                    "_DEBUG",
                    "UNICODE",
                    "_UNICODE"
                ]
            }
        ],
        "version": 4
    }
    return json.dumps(c_cpp_json, indent=4)


def get_include_paths(libraries):
    c_flags = []
    for lib in libraries:
        try:
            c_flags += pkgconfig.cflags(lib).split(" ")
        except Exception as e:
            pass
    include_paths = []
    for flag in c_flags:
        strip_flag = flag.strip()
        if strip_flag[0:2] == "-I":
            include_paths.append(strip_flag[2:])
    return list(set(include_paths))
