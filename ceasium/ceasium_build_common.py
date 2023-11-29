import os
from .ceasium_config import read_config
import pkgconfig
import shutil


def gen_linker_flags(build_config):
    flags = gen_linker_flags_recursive(build_config)
    flags += build_config['flags']['linker']
    flags.sort()
    return " ".join(flags)


def gen_linker_flags_and_copy(build_config, path):
    flags = gen_linker_flags_recursive_and_copy(build_config, path)
    flags += build_config['flags']['linker']
    flags.sort()
    return " ".join(flags)


def gen_linker_flags_recursive(build_config):
    dependencies = build_config.get("depends-on", [])
    flags = []
    for dependency in dependencies:
        dependency_config = read_config(dependency)
        flags += gen_pkg_config_linker_flags(dependency_config["libraries"])
        flags += gen_compiler_flags_recursive(dependency_config)
        flags += [f"-l{dependency_config['name']}"]
    return list(set(flags))


def gen_linker_flags_recursive_and_copy(build_config, path):
    dependencies = build_config.get("depends-on", [])
    flags = []
    for dependency in dependencies:
        dependency_config = read_config(dependency)
        flags += gen_pkg_config_linker_flags(dependency_config["libraries"])
        flags += gen_linker_flags_recursive_and_copy(dependency_config, path)
        flags += [f"-l{dependency_config['name']}"]
        lib_dir = os.path.join(dependency, "build")
        flags += [f"-L{lib_dir}"]
        lib_path = os.path.join(lib_dir, f'{dependency_config["name"]}.dll')
        dest = os.path.join(path, f'{dependency_config["name"]}.dll')
        shutil.copyfile(lib_path, dest)
    return list(set(flags))


def gen_pkg_config_linker_flags(libraries):
    lib_flags = []
    if len(libraries) > 0:
        for lib in libraries:
            try:
                lib_flags += pkgconfig.libs(lib).split(" ")
            except Exception:
                pass
        return lib_flags
    else:
        return []


def gen_compiler_flags(build_config):
    flags = gen_compiler_flags_recursive(build_config)
    flags += build_config['flags']['compiler']
    flags.sort()
    return " ".join(flags)


def gen_compiler_flags_recursive(build_config):
    dependencies = build_config.get("depends-on", [])
    flags = []
    for dependency in dependencies:
        dependency_config = read_config(dependency)
        include_path = os.path.join(dependency, "include")
        flags.append(f"-I{include_path}")
        flags += gen_pkg_config_flags(dependency_config["libraries"])
        flags += gen_compiler_flags_recursive(dependency_config)
    return list(set(flags))


def gen_pkg_config_flags(libraries):
    cflags = []
    if len(libraries) > 0:
        for lib in libraries:
            try:
                cflags += pkgconfig.cflags(lib).split(" ")
            except Exception:
                pass
        return cflags
    else:
        return []
