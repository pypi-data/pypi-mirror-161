from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.sfy_init.pack import Pack


class NoPack(Pack):
    def ask_questions(self, input_hook: InputHook, output_hook: OutputCallBack):
        pass

    def get_default_service_name(self):
        return "my-service"

    def get_description(self):
        return None

    def get_files(self):
        return {}
