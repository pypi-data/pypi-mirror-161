from mako.template import Template

from servicefoundry.requirements.python_requirements import PythonRequirements
from servicefoundry.sfy_magic_init_pack.magic_pack import MagicPack
from servicefoundry.sfy_magic_init_pack.util import get_module_name_from_python_file

main_file_content = """
from ${module_name} import app

app.launch(server_name="0.0.0.0", server_port=8000)
"""

requirements_txt_content = """
# ServicefoundryManaged
gradio
"""


class GradioMagicPack(MagicPack):
    def get_files(self):
        main_file_rendered_content = Template(main_file_content).render(
            module_name=get_module_name_from_python_file(self.python_file)
        )
        requirements = PythonRequirements(requirements_txt_content)
        requirements.update_requirements_txt(self.additional_requirements)
        return {
            "main.py": main_file_rendered_content,
            "requirements.txt": requirements.get_requirements_txt(),
            "Procfile": "web: python main.py",
        }
