import sys

from dagster_fmt import run

if __name__ == "__main__":
    # TODO: CLI
    file_name = sys.argv[1]
    run(file_name)
