class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class PathValidationException(ValidationException):
    def __init__(self, path, message):
        path = make_path(path)
        super().__init__(f"{path} {message}.")


def validate():
    pass


def validate_build_json_for_build(json, build_key):
    build_path = ['build', build_key]
    build = access(json, build_path)
    validate_dict(
        build,
        build_path,
        ["compile", "link"],
        [],
        lambda value, path: validate_build(value, path, json)
    )
    validate_compile_link_all(json, ["compile"])
    validate_compile_link_all(json, ["link"])
    libs = json.get("libs")
    validate_dict(
        libs,
        ["libs"],
        libs.keys(),
        [],
        validate_libs
    )


def validate_libs(value, path):
    validate_dict(
        value,
        path,
        ["name", "version"],
        ["name", "version"],
        lambda x, p: validate_type(x, p, str)
    )


def validate_compile_link_all(json, path):
    obj = access(json, path)
    validate_type(obj, path, dict)
    for key in obj:
        validate_dict(
            obj[key],
            path + [key],
            ["cflags", "dirs", "ldflags", "libs", "cc"],
            ["dirs"],
            lambda value, path: validate_compile_link(value, path, json)
        )


def validate_compile_link(value, path, json):
    if path[-1] in ["libs", "dirs"]:
        validate_list(value, path, lambda x, path: validate_type(x, path, str))
    if path[-1] in ["cflags", "ldflags"]:
        validate_list_of_flags(value, path)
    if path[-1] == "libs":
        libs = access(json, ["libs"])
        validate_dict(
            libs,
            ["libs"],
            libs.keys(),
            value,
            lambda a, b: True
        )
    validate_at_least_one(
        json,
        [
            path + ["cc"],
            ["cc"]
        ]
    )


def validate_build(value, path, json):
    if len(path) == 3:
        validate_list(
            value,
            path,
            lambda x, path:
                validate_type(x, path, str) and
                access(json, [path[-1], x])
        )


def make_path(path):
    path = [str(p) for p in path]
    return ":".join(["root", *path])


def validate_at_least_one(json, paths):
    for path in paths:
        try:
            access(json, path)
            return
        except PathValidationException:
            pass
    paths_str = [make_path(path) for path in paths]
    raise ValidationException(f"At least one in {paths_str} must exist.")


def validate_list_of_flags(flags, path):
    validate_list(flags, path, validate_flag)


def validate_flag(flag, path):
    validate_type(flag, path, str)
    if not flag.startswith("-"):
        raise PathValidationException(path, "is not a valid flag")


def validate_dict(obj, path, valid_keys, required_keys, validate):
    validate_type(obj, path, dict)
    for key in required_keys:
        if key not in obj:
            raise PathValidationException(path + [key], "is required")
    for key in obj:
        key_path = path + [key]
        if key not in valid_keys:
            raise PathValidationException(key_path, "is not valid")
        validate(obj[key], key_path)


def validate_not_empty(elements, path):
    if len(elements) == 0:
        raise PathValidationException(path, "cannot be empty")


def validate_list(elements, path, validate):
    validate_type(elements, path, list)
    for element in elements:
        validate(element, path + [element])


def validate_type(value, path, target_type):
    if type(value) != target_type:
        raise PathValidationException(
            path, f"must be a {target_type.__name__} but is {type(value).__name__}"
        )


def access(json, path):
    value = json
    current_path = []
    for subpath in path:
        validate_type(value, current_path, dict)
        current_path.append(subpath)
        if subpath not in value:
            raise PathValidationException(current_path, "is missing")
        value = value[subpath]
    return value
