root_keys = set(["libs", "cflags", "cc", "compile", "link", "build"])
build_keys = set(['compile', 'link'])
compile_keys = set(["cflags", "dirs", "libs"])


class ValidationException(Exception):
    def __init__(self, path, message):
        path = ":".join(path)
        super().__init__(f"{path} {message}.")


class RequiredException(ValidationException):
    def __init__(self, path):
        super().__init__(path, "is required")


class TypeException(ValidationException):
    def __init__(self, path, type):
        super().__init__(path, f"must be a {type}")


def validate_object(
    path,
    valid_keys,
    required_keys,
    obj
):
    validate_required_keys(path, obj, required_keys)
    validate_keys(path, obj, valid_keys)


def validate_required_keys(path, obj, keys):
    for key in keys:
        if key not in obj:
            raise RequiredException(path)


def validate_keys(path, obj, keys):
    for key in obj:
        if key not in keys:
            raise Exception(f"{path}:{key} is not a valid key.")


def validate_build_json(build):
    validate_keys(".", build, root_keys)
    validate_all_libs(build)


def validate_all_libs(build):
    if 'libs' in build:
        for lib in build['libs']:
            libval = build['libs'][lib]
            if type(libval) != dict:
                raise Exception(f"libs:{lib} must be a dictionary.")
            validate_required_keys(f"libs:{lib}", libval, ["name", "version"])


def validate_build_json_for_build(build_json, subcommand):
    validate_object([], root_keys, ["build"], build_json)
    path = ['build']
    build = build_json['build']
    validate_object(path, root_keys, [subcommand], build_json)
    build_subcommand = build[subcommand]
    path.append(subcommand)
    validate_keys(path, build_subcommand, build_keys)
    build_compiles = build_subcommand.get('compile', [])
    compile_path = path = ["compile"]
    validate_array_of_strings(compile_path, build_compiles)
    validate_array_of_strings(["cflags"], build_json.get("cflags", []))
    validate_flags(["cflags"], build_json.get("cflags", []))
    validate_string(["cc"], build_json.get("cc", ""))
    # for compile_name in build_compiles:
    #     validate_common(
    #         "compile",
    #         compile_name,
    #         build_json,
    #         build_compiles
    #     )
    # for link_name in build_subcommand["link"]:
    #     validate_common(
    #         "link",
    #         link_name,
    #         build_json,
    #         build_subcommand["link"],
    #         ["cflags", "dirs", "libs", "cc", "ldflags"]
    #     )
    #     validate_flags(
    #         f"link:{link_name}:ldflags",
    #         build_json["link"][link_name].get("ldflags", [])
    #     )


def validate_common(
    node,
    subnode,
    root,
    keys,
    valid_keys=["cflags", "dirs", "libs", "cc"]
):
    validate_required_keys(node, root, [node])
    value = root[node]
    validate_required_keys(node, value, keys)
    validate_keys([node, subnode], value[subnode], valid_keys)
    validate_flags([node, subnode, "cflags"], value[subnode].get("cflags", []))
    validate_dirs([node, subnode], value[subnode])
    validate_libs([node, subnode], root, value[subnode])
    # validate_compiler(
    #     f"{node}:{subnode}", root, value[subnode]
    # )


# def validate_compiler(p, root, node):
#     validate_string(f"{p}:cc", node.get("cc", ""))
#     validate_at_least_one(
#         [
#             (f"cc", root.get("cc", None)),
#             (f"{p}:cc", node.get("cc", None))
#         ]
#     )


# def validate_at_least_one(arr):
#     for (_, a) in arr:
#         if a != None:
#             return
#     raise Exception(
#         f"At least one must be defined: {[p for (p, _) in (arr)]}.")

def validate_dirs(path, comp):
    validate_required_keys(path, comp, ["dirs"])
    dirs = path + ['dirs']
    validate_array_of_strings(dirs, comp.get("dirs", []))
    validate_not_empty(dirs, comp.get("dirs"))


def validate_libs(path, build_json, o):
    validate_array_of_strings(
        path + ['libs'], o.get("libs", [])
    )
    validate_required_keys(
        ['libs'],
        build_json.get('libs', {}),
        o.get('libs', [])
    )


def validate_not_empty(path, arr):
    if len(arr) == 0:
        raise ValidationException(path, "cannot be empty.")


def validate_flags(path, list_of_flags):
    validate_array_of_strings(path, list_of_flags)
    for flag in list_of_flags:
        if not flag.startswith("-"):
            raise ValidationException(path + [flag], "is not a flag")


def validate_array_of_strings(path, obj):
    if type(obj) != list:
        raise TypeException(path, list)
    for key in obj:
        validate_string(path + [key], key)


def validate_string(path, obj):
    if type(obj) != str:
        raise TypeException(path, str)
