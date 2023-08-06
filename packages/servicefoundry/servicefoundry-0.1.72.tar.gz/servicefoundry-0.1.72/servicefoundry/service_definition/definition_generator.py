from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.io.parameters import Parameter, WorkspaceParameter
from servicefoundry.service_definition.definition import ServiceFoundryDefinition

MB = 1000 * 1000


# TODO (chiragjn): Add validation for all the fields asked from customer
# TODO (chiragjn): support more complex schema like "0.0.0.0:8000:80/TCP"
class ServiceFoundryDefinitionGenerator:
    def __init__(
        self,
        input_hook: InputHook,
        output_hook: OutputCallBack,
        base_definition: ServiceFoundryDefinition,
    ):
        self.input_hook = input_hook
        self.output_hook = output_hook
        self.definition = base_definition

    def _ask_and_set_service_name(self, default):
        if not default:
            default = self.definition.service.name
        param = Parameter(
            prompt="Name your service (min 5 characters)", default=default
        )
        service_name = self.input_hook.ask_string(param)
        self.definition.service.name = service_name

    def _ask_and_set_workspace(self):
        prompt = "Choose a workspace to deploy your service"
        workspace_fqn = self.input_hook.ask_workspace(WorkspaceParameter(prompt=prompt))
        self.definition.service.workspace = workspace_fqn

    def _ask_and_set_cpu_required(self):
        prompt = "Minimum amount of CPU to allocate (1 = 1 physical/virtual core, min 0.0001)"
        cpu_required = self.input_hook.ask_float(
            Parameter(prompt=prompt, default=self.definition.service.cpu.required)
        )
        self.definition.service.cpu.required = cpu_required
        if cpu_required > self.definition.service.cpu.limit:
            self.definition.service.cpu.limit = cpu_required

    def _ask_and_set_memory_required(self):
        prompt = "Minimum amount of memory to allocate (in MB, min 1)"
        mem_required = (
            self.input_hook.ask_integer(
                Parameter(
                    prompt=prompt,
                    default=int(self.definition.service.memory.required / MB),
                )
            )
            * MB
        )
        self.definition.service.memory.required = mem_required
        if mem_required > self.definition.service.memory.limit:
            self.definition.service.memory.limit = mem_required

    def _ask_and_set_replicas(self):
        prompt = "Choose a number of replicas for your service"
        replicas = self.input_hook.ask_integer(
            Parameter(prompt=prompt, default=self.definition.service.replicas)
        )
        self.definition.service.replicas = replicas

    def _ask_and_set_port(self):
        prompt = "Choose a port to expose for your service"
        port = self.input_hook.ask_integer(
            Parameter(
                prompt=prompt, default=self.definition.service.ports[0].containerPort
            )
        )
        self.definition.service.ports[0].containerPort = port

    def ask_questions(self, default_service_name):
        self._ask_and_set_service_name(default=default_service_name)
        self._ask_and_set_workspace()
        prompt = (
            f"Would you like to change additional parameter? "
            f"CPU required = {self.definition.service.cpu.required}, "
            f"Memory Required = {int(self.definition.service.memory.required/MB)} MB, "
            f"Service Port = {self.definition.service.ports[0].containerPort}, "
            f"Replicas = {self.definition.service.replicas}"
        )
        if self.input_hook.confirm(prompt):
            self._ask_and_set_cpu_required()
            self._ask_and_set_memory_required()
            self._ask_and_set_port()
            self._ask_and_set_replicas()
