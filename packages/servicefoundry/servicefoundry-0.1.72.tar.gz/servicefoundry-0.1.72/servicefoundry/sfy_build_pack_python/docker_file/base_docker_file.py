from typing import List

from mako.template import Template

from servicefoundry.sfy_build_pack_python.docker_file.layer import Layer

PYTHON_37 = "python:3.7"
PYTHON_38 = "python:3.8"
PYTHON_39 = "python:3.9"
PYTHON_310 = "python:3.10"


class BaseDockerFile(object):
    def __init__(self, layers: List[Layer], base_image):
        if len(layers) == 0:
            raise ValueError("Modules should contain at least one module")
        self.layers = layers
        self.base_image = base_image

    def to_dockerfile(self):
        entrypoint = None
        for layer in self.layers:
            if layer.entrypoint():
                entrypoint = layer.entrypoint()

        template = Template(
            """
            # Layer list: ${','.join([layer.name() for layer in layers])}
            FROM ${base_image}

            % for layer in layers:
            # ${layer.name()} start
            ${layer.build()}
            # ${layer.name()} end
            % endfor

            COPY . /code
            WORKDIR /code
            ENTRYPOINT ${entrypoint}
        """
        )
        return template.render(
            base_image=self.base_image, layers=self.layers, entrypoint=entrypoint
        )
