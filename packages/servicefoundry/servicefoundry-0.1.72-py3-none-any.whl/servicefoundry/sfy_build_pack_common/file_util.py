from pathlib import Path


def write_file(file, text):
    with open(file, "w") as text_file:
        text_file.write(text)


def create_dir(directory):
    return Path(directory).mkdir(parents=True, exist_ok=True)
