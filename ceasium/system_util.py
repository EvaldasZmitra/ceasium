import os
import subprocess
import time


def execute(cmd):
    popen = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def run_command(command):
    result = ""
    for l in execute(command):
        try:
            result += l
        except Exception as e:
            pass
    return result


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def remove_trailing_backslash(input_string):
    if input_string.endswith("\\"):
        return input_string[:-1]
    else:
        return input_string


def get_output(command):
    return subprocess.run(
        " ".join(command),
        shell=True,
        capture_output=True,
        universal_newlines=True
    ).stdout


def run_timed(command):
    start = time.time()
    o = subprocess.run(
        " ".join(command),
        shell=True,
        capture_output=True,
        universal_newlines=True
    )
    if o.returncode != 0:
        raise Exception(o.stderr)
    run_command(" ".join(command))
    return {
        "result": o.stderr,
        "time": time.time() - start,
    }
