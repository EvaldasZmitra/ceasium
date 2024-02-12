import os
import shutil
from ..constants import build_folder_name


def clean(args):
    build_path = os.path.join(args.path, build_folder_name)
    shutil.rmtree(build_path)
