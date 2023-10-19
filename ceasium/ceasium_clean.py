import os
import shutil


build_folder_name = "build"


def clean(args):
    build_path = os.path.join(args.path, build_folder_name)
    shutil.rmtree(build_path)
