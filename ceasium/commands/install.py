import subprocess
from ..config import read_config
from ..system_util import run_command


libraries = {
    "allegro": {
        "apt": "liballegro5-dev"
    },
    "ao": {
        "apt": "libao-dev"
    },
    "blosc": {
        "apt": "libblosc-dev"
    },
    "brotli": {
        "apt": "libbrotli-dev"
    },
    "cairo": {
        "apt": "libcairo2-dev"
    },
    "cglm": {
        "apt": "libcglm-dev"
    },
    "chipmunk": {
        "apt": "libchipmunk-dev"
    },
    "csfml": {
        "apt": "libcsfml-dev"
    },
    "darkplaces": {
        "apt": "darkplaces-server"
    },
    "epoxy": {
        "apt": "libepoxy-dev"
    },
    "freecell-solver": {
        "apt": "libfreecell-solver-dev"
    },
    "freeglut": {
        "apt": "freeglut3-dev"
    },
    "gd-2.0": {
        "apt": "libgd-dev"
    },
    "gl": {
        "apt": "libgl1-mesa-dev"
    },
    "glfw3": {
        "apt": "libglfw3-dev"
    },
    "glib-2.0": {
        "apt": "libc6-dev"
    },
    "groonga": {
        "apt": "libgroonga-dev"
    },
    "gtk+-3.0": {
        "apt": "libgtk-3-dev"
    },
    "highwayhash": {
        "apt": "libhighwayhash-dev"
    },
    "hiredis": {
        "apt": "libhiredis-dev"
    },
    "ioquake3": {
        "apt": "ioquake3"
    },
    "libarchive": {
        "apt": "libarchive-dev"
    },
    "libavl": {
        "apt": "libavl-dev"
    },
    "libbz2": {
        "apt": "libbz2-dev"
    },
    "libcaca": {
        "apt": "libcaca-dev"
    },
    "libdb": {
        "apt": "libdb-dev"
    },
    "libgif": {
        "apt": "libgif-dev"
    },
    "glew": {
        "apt": "libglew-dev"
    },
    "libimagequant": {
        "apt": "libimagequant-dev"
    },
    "libjpeg": {
        "apt": "libjpeg-dev"
    },
    "liblmdb": {
        "apt": "liblmdb-dev"
    },
    "liblz4": {
        "apt": "liblz4-dev"
    },
    "libmongoc-1.0": {
        "apt": "libmongoc-dev"
    },
    "libomp": {
        "apt": "libomp-dev"
    },
    "libopenmpi": {
        "apt": "libopenmpi-dev"
    },
    "libpng": {
        "apt": "libpng-dev"
    },
    "libpq": {
        "apt": "libpq-dev"
    },
    "librsvg-2.0": {
        "apt": "librsvg2-dev"
    },
    "libsixel": {
        "apt": "libsixel-dev"
    },
    "libspng": {
        "apt": "libspng-dev"
    },
    "liburcu": {
        "apt": "liburcu-dev"
    },
    "libzip": {
        "apt": "libzip-dev"
    },
    "libzstd": {
        "apt": "libzstd-dev"
    },
    "lzo2": {
        "apt": "liblzo2-dev"
    },
    "mozjs-78": {
        "apt": "libmozjs-78-dev (Note: Check compatibility)"
    },
    "mysqlclient": {
        "apt": "libmysqlclient-dev"
    },
    "opencl": {
        "apt": "ocl-icd-opencl-dev"
    },
    "pth": {
        "apt": "libpth-dev"
    },
    "pthread": {
        "apt": "libc6-dev"
    },
    "quake": {
        "apt": "quake"
    },
    "retroarch": {
        "apt": "retroarch"
    },
    "roaring": {
        "apt": "libroaring-dev"
    },
    "sdl": {
        "apt": "libsdl1.2-dev"
    },
    "sdl2": {
        "apt": "libsdl2-dev"
    },
    "sqlite3": {
        "apt": "libsqlite3-dev"
    },
    "tk": {
        "apt": "tk-dev"
    },
    "vips": {
        "apt": "libvips-dev"
    },
    "xxhash": {
        "apt": "libxxhash-dev"
    },
    "yamagi-quake2": {
        "apt": "yamagi-quake2"
    },
    "zlib": {
        "apt": "zlib1g-dev"
    }
}


def install(args):
    build_config = read_config(args.path)
    for library_pkg_conf in build_config['libraries']:
        if library_pkg_conf in libraries:
            lib = libraries[library_pkg_conf]
            if args.package_manager in lib:
                true_lib = lib[args.package_manager]
                if args.package_manager == "apt":
                    subprocess.run(
                        f"sudo apt -y install {true_lib}",
                        shell=True,
                        universal_newlines=True
                    )
    for package in build_config["packages"][args.package_manager]:
        run_command(package)
