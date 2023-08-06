import os

name = "sfy_build_pack_docker"


def detect(**kwargs):
    print(f"Build pack {name} is looking for a Dockerfile.")
    if os.path.isfile("Dockerfile"):
        print(f"Build pack {name} can build this project. Found a Dockerfile.")
        return True
    print(f"Build pack {name} can't build this project. Can't find a Dockerfile.")
    return False
