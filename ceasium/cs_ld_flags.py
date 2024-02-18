import argparse
import pkgconfig
from os.path import abspath


def main():
    parser = argparse.ArgumentParser(
        description='Description of your script.')
    parser.add_argument('libs', nargs='+')
    args = parser.parse_args()
    flags = pkgconfig.libs(" ".join(args.libs)).split(" -")
    if len(flags) > 1:
        flags = [flags[0]] + [f"-{lib}" for lib in flags[1:]]
    true_flags = []
    for flag in flags:
        flag = flag.strip()
        if flag.startswith("-L"):
            true_flags.append(f"-L{abspath(flag[2:])}")
        elif flag.startswith("-I"):
            true_flags.append(f"-I{abspath(flag[2:])}")
        else:
            true_flags.append(flag)

    print(" ".join(true_flags))
    return 1


if __name__ == "__main__":
    main()
