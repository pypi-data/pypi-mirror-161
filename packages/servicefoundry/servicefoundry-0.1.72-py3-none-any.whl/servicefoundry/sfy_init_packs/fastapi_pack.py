from servicefoundry.sfy_init_packs.python_base_pack import PythonBasePack

main_file_content = """
import logging
import os
from fastapi.responses import HTMLResponse
from servicefoundry.service import fastapi

logger = logging.getLogger(__name__)
app = fastapi.app()


@app.get(path="/add")
def add(a: int, b: int):
    return a + b


@app.get("/", response_class=HTMLResponse)
def root():
    html_content = "<html><body>Open <a href='/docs'>Docs</a></body></html>"
    return HTMLResponse(content=html_content, status_code=200)

"""

requirements_txt_content = """
# ServicefoundryManaged
servicefoundry>=0.1.34,<0.2.0
fastapi>=0.78.0,<1.0.0
prometheus_client>=0.14.1,<1.0.0
uvicorn>=0.17.0,<1.0.0
"""


class FastApiPack(PythonBasePack):
    def get_default_service_name(self):
        return "fastapi-service"

    def get_description(self):
        return "fastapi - Create REST service using fastapi framework."

    def get_files(self):
        return {
            "main.py": main_file_content,
            "requirements.txt": requirements_txt_content,
            "Procfile": "web: uvicorn main:app --host 0.0.0.0 --port 8000",
        }
