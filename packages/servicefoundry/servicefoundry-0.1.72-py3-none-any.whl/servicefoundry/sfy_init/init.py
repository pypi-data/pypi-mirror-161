from pathlib import Path

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import OptionsParameter
from servicefoundry.service_definition.definition_generator import (
    ServiceFoundryDefinitionGenerator,
)
from servicefoundry.sfy_init.init_flow import InitTemplateFlow
from servicefoundry.sfy_init.init_pack import get_init_pack
from servicefoundry.sfy_init.no_pack import NoPack
from servicefoundry.sfy_init.pack import Pack
from servicefoundry.sfy_init.util import _maybe_backup_file


def init(
    input_hook: InputHook,
    output_hook: OutputCallBack,
    definition_filename="servicefoundry.yaml",
    directory="./",
):
    init_pack: Pack = NoPack()
    directory = Path(directory).resolve()
    default_service_name = directory.name
    definition_gen = ServiceFoundryDefinitionGenerator(
        input_hook=input_hook,
        output_hook=output_hook,
        base_definition=init_pack.get_default_definition(),
    )
    definition_gen.ask_questions(default_service_name=default_service_name)
    definition_path = directory / definition_filename
    _maybe_backup_file(
        file_path=definition_path, input_hook=input_hook, output_hook=output_hook
    )
    definition_gen.definition.to_yaml(definition_path)


def init_from_template(
    input_hook: InputHook,
    output_hook: OutputCallBack,
    definition_filename="servicefoundry.yaml",
    base_directory=Path("./"),
):
    params = OptionsParameter(prompt="Choose a template", options=get_init_pack())
    init_pack: Pack = input_hook.ask_option(params)
    init_flow = InitTemplateFlow(
        init_pack, input_hook, output_hook, base_directory, definition_filename
    )
    init_flow.ask_question()
    init_flow.create_project()
