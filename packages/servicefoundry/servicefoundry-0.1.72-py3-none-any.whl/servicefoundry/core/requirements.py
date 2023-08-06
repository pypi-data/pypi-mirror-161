from servicefoundry.requirements.interceptor.interceptor import Interceptor


def gather_requirements(python_file):
    return Interceptor.create(python_file).get_dependencies()
