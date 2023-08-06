from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import Parameter
from servicefoundry.service_definition.definition import (
    Port,
    ServiceFoundryBuildDefinition,
    ServiceFoundryDefinition,
)
from servicefoundry.sfy_init.pack import Pack

docker_file_content = """
# This file is generated from service foundry. Don't make changes directly.
FROM tensorflow/serving
ENV MODEL_NAME={model_name}
COPY {model_name} /models/{model_name}/1
"""

readme_content = """
* Create a new directory named `{model_name}` inside this directory
* Put your SavedModel artifacts (assets, variables, saved_model.pb etc) in the new directory
* Run `sfy deploy` to deploy the service
"""


class TfServePack(Pack):
    model_name = None

    def ask_questions(self, input_hook: InputHook, output_hook: OutputCallBack):
        param = Parameter(prompt="Name of your model?")
        self.model_name = input_hook.ask_string(param)

    def get_default_service_name(self):
        return "tensorflow-service"

    def get_description(self):
        return "tensorflow-serving - Deploy a TensorFlow SavedModel"

    def get_default_definition(self) -> ServiceFoundryDefinition:
        definition = super().get_default_definition()
        definition.build = ServiceFoundryBuildDefinition(
            build_pack="sfy_build_pack_docker",
        )
        definition.service.ports = [Port(containerPort=8501)]
        return definition

    def get_files(self):
        return {
            "Dockerfile": docker_file_content.format(model_name=self.model_name),
            "readme.txt": readme_content.format(model_name=self.model_name),
        }
