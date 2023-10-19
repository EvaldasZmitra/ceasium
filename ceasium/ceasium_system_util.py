import os
import os
import subprocess


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
    print(command)
    for line in execute(command):
        print(line, end="")


def remove_trailing_backslash(input_string):
    if input_string.endswith("\\"):
        return input_string[:-1]
    else:
        return input_string
