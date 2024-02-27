import os
from .constants import colors


def print_red(text):
    print(f"{colors.RED}{text}{colors.RESET}")


def print_green(text):
    print(f"{colors.GREEN}{text}{colors.RESET}")


def print_grey(text):
    print(f"{colors.DARK_GREY}{text}{colors.RESET}")


def print_yellow(text):
    print(f"{colors.YELLOW}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


def write_if_not_exists(path, text):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(text)
