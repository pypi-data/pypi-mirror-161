import os

from servicefoundry.lib.exceptions import ConfigurationException


# TODO @cloud take care of file inside directory
def get_module_name_from_python_file(file_name):
    if file_name.endswith(".py"):
        return file_name[0:-3].replace(os.sep, ".")
    raise ConfigurationException(f"{file_name} doesn't end with py")
