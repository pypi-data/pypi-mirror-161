from mako.template import Template

from servicefoundry.requirements.python_requirements import PythonRequirements
from servicefoundry.sfy_magic_init_pack.magic_pack import MagicPack
from servicefoundry.sfy_magic_init_pack.util import get_module_name_from_python_file

main_file_content = """
from inspect import getmembers, isfunction
import logging
from fastapi.responses import HTMLResponse
from servicefoundry.service import fastapi
try:
    import ${module_name} as functions
except ImportError as error:
    print("Failed to import function ${module_name}: " + str(error))
    raise error

logger = logging.getLogger(__name__)
app = fastapi.app()


@app.get("/", response_class=HTMLResponse)
def root():
    html_content = "<html><body>Open <a href='/docs'>Docs</a></body></html>"
    return HTMLResponse(content=html_content, status_code=200)

for name, func in getmembers(functions, predicate=isfunction):
    app.add_api_route("/" + name, func, methods=["POST"])
"""

requirements_txt_content = """
# ServicefoundryManaged
servicefoundry
fastapi==0.78.0
prometheus_client
uvicorn
"""


class AutoServiceMagicPack(MagicPack):
    def get_files(self):
        main_file_rendered_content = Template(main_file_content).render(
            module_name=get_module_name_from_python_file(self.python_file)
        )
        requirements = PythonRequirements(requirements_txt_content)
        requirements.update_requirements_txt(self.additional_requirements)
        return {
            "main.py": main_file_rendered_content,
            "requirements.txt": requirements.get_requirements_txt(),
            "Procfile": "web: uvicorn main:app --host 0.0.0.0 --port 8000",
        }
