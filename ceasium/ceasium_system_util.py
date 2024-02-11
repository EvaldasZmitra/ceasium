import os
import subprocess

colors_arr = [
    '\033[0m',
    '\033[91m',
    '\033[92m',
    '\033[93m',
    '\033[94m',
    '\033[95m',
    '\033[96m',
    '\033[97m',
    '\033[1m',
    '\033[4m',
    '\033[37m',
    '\033[90m'
]


class colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    LIGHT_GREY = '\033[37m'
    DARK_GREY = '\033[90m'


def print_red(text):
    print(f"{colors.RED}{text}{colors.RESET}")


def print_green(text):
    print(f"{colors.GREEN}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.RESET}")


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def write_if_not_exists(path, text):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(text)


def find_files(base_path, relative_path=""):
    files = []
    path = base_path
    if relative_path != "":
        path = os.path.join(path, relative_path)
    for filename in os.listdir(path):
        added_path = os.path.join(path, filename)
        if os.path.isfile(added_path) and filename[-2:] == ".c":
            files.append((relative_path, filename))
        if os.path.isdir(added_path):
            new_relative_path = os.path.join(relative_path, filename)
            files = files + find_files(base_path, new_relative_path)
    return files


def run_command(command):
    result = ""
    for l in execute(command):
        try:
            result += l
        except Exception as e:
            pass
    return result


def run_gcc_command(command):
    true_cmd = command.replace(os.linesep, " ").replace(os.linesep, " ")
    for value in colors_arr:
        true_cmd = true_cmd.replace(value, "")
    # v = run_command(true_cmd)
    # return v
    err = subprocess.run(
        true_cmd,
        shell=True,
        capture_output=True,
        universal_newlines=True
    ).stderr
    return err


def remove_trailing_backslash(input_string):
    if input_string.endswith("\\"):
        return input_string[:-1]
    else:
        return input_string
