import pkgconfig


def gen_pkg_config_linker_flags(libraries):
    libFlags = []
    if len(libraries) > 0:
        for lib in libraries:
            try:
                libFlags += pkgconfig.libs(lib).split(" ")
            except Exception:
                pass
        return libFlags
    else:
        return []


def gen_pkg_config_cc_flags(libraries):
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
