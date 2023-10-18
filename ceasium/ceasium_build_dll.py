import os

from .ceasium_system_util import run_command


def build_dynamic_lib(build_path, o_files, build_config):
    library_path = os.path.join(build_path, f"{build_config['name']}.dll")
    cc = build_config["compiler"]
    command = f'{cc} -shared -o {library_path} {" ".join(o_files)}'
    run_command(command)
