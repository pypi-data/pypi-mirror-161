from abc import ABC, abstractmethod

from servicefoundry.io.parameters import OptionsParameter, Parameter, WorkspaceParameter


class InputHook(ABC):
    @abstractmethod
    def confirm(self, prompt, default=False):
        pass

    @abstractmethod
    def ask_string(self, param: Parameter):
        pass

    @abstractmethod
    def ask_number(self, param: Parameter):
        pass

    def ask_integer(self, param: Parameter):
        return self.ask_number(param)

    def ask_float(self, param: Parameter):
        return self.ask_number(param)

    @abstractmethod
    def ask_file_path(self, param: Parameter):
        pass

    @abstractmethod
    def ask_option(self, param: OptionsParameter):
        pass

    @abstractmethod
    def ask_workspace(self, param: WorkspaceParameter):
        pass

    @abstractmethod
    def ask_python_file(self, param: Parameter):
        pass


class FailInputHook(InputHook):
    def confirm(self, prompt, default=False):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_boolean"
        )

    def ask_string(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_string"
        )

    def ask_number(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )

    def ask_file_path(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_number"
        )

    def ask_option(self, param: OptionsParameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_option"
        )

    def ask_workspace(self, param: WorkspaceParameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_workspace"
        )

    def ask_python_file(self, param: Parameter):
        raise NotImplementedError(
            f"{InputHook.__name__} doesn't implement method ask_file"
        )
