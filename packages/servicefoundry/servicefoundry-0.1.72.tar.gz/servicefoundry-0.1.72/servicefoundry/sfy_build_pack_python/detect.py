import os

pack_name = "sfy_build_pack_python"


def detect(**kwargs):
    print(f"Build pack {pack_name} looking for Procfile and requirements.txt.")
    if os.path.isfile("requirements.txt"):
        if os.path.isfile("Procfile"):
            print(
                f"Build pack {pack_name} can build this project. Found both Procfile and requirements.txt."
            )
            return True
        print(
            f"Build pack {pack_name} can't build this project. "
            f"Found requirements.txt file, but can't find Procfile."
        )
        return False
    print(
        f"Build pack {pack_name} can't build this project. "
        f"Can't find requirements.txt or Procfile."
    )
    return False
