from servicefoundry.sfy_build_pack_python.docker_file.layer import Layer


class Requirements(Layer):
    def build(self):
        return "\n".join(
            [
                "COPY requirements.txt requirements.txt",
                "RUN pip install --upgrade pip",
                "RUN pip install --no-cache-dir --upgrade -r requirements.txt",
            ]
        )
