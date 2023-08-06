from servicefoundry.auto_gen.models import DockerFileBuildConfig, constr


# Evil
class DockerFileBuildConfig(DockerFileBuildConfig):
    type: constr(regex=r"dockerfile") = "dockerfile"
