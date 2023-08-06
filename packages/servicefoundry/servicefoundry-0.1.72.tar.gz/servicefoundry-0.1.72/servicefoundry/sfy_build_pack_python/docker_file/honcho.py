from servicefoundry.sfy_build_pack_python.docker_file.layer import Layer


class Honcho(Layer):
    def __repr__(self):
        return ""

    def build(self):
        return f"RUN pip install honcho"

    def entrypoint(self):
        return f"honcho start"
