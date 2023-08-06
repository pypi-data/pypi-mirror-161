import shutil
from pathlib import Path
from typing import Dict

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.service_definition.definition_generator import (
    ServiceFoundryDefinitionGenerator,
)
from servicefoundry.sfy_init.pack import Pack
from servicefoundry.sfy_init.util import _maybe_backup_file
from servicefoundry.utils.file_utils import create_file_from_content


class InitTemplateFlow:
    def __init__(
        self,
        pack: Pack,
        input_hook: InputHook,
        output_hook: OutputCallBack,
        base_directory: Path,
        definition_filename="servicefoundry.yaml",
        is_cli=True,
    ):
        self.pack = pack
        self.input_hook = input_hook
        self.output_hook = output_hook
        self.definition_filename = definition_filename
        self.base_directory = base_directory
        self.is_cli = is_cli

    def ask_question(self):
        self.pack.ask_questions(self.input_hook, self.output_hook)

    def create_project(self):
        default_service_name = self.pack.get_default_service_name()
        definition_gen = ServiceFoundryDefinitionGenerator(
            input_hook=self.input_hook,
            output_hook=self.output_hook,
            base_definition=self.pack.get_default_definition(),
        )
        if self.is_cli:
            definition_gen.ask_questions(default_service_name=default_service_name)
        return self._create_project(definition_gen.definition)

    def _create_project(self, definition):
        directory = self.base_directory / definition.service.name
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        directory = directory.resolve()
        self._create_directory(directory)
        definition_path = directory / self.definition_filename
        _maybe_backup_file(
            file_path=definition_path,
            input_hook=self.input_hook,
            output_hook=self.output_hook,
        )
        definition.to_yaml(definition_path)
        self.output_hook.print_line(
            f"Created definition file {definition_path.resolve()}"
        )
        self._create_init_pack_files(directory)
        return directory

    def _create_directory(self, directory):
        if not self.is_cli:
            shutil.rmtree(directory)
        if not directory.exists():
            self.output_hook.print_line(f"Creating directory {directory.resolve()}")
            directory.mkdir(parents=True, exist_ok=True)

    def _create_init_pack_files(self, directory):
        files: Dict[str, str] = self.pack.get_files()
        for file, content in files.items():
            file_path = directory / file
            _maybe_backup_file(
                file_path=file_path,
                input_hook=self.input_hook,
                output_hook=self.output_hook,
            )
            create_file_from_content(file_path, content)
            self.output_hook.print_line(f"Created file {file_path.resolve()}")
