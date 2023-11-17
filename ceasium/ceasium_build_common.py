def gen_compiler_flags(build_config):
    return gen_explicit_compiler_flags(
        build_config['flags']['compiler']
    )


def gen_explicit_compiler_flags(flags):
    return " ".join(flags)
