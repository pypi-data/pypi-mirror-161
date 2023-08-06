from mako.template import Template

from servicefoundry.requirements.python_requirements import PythonRequirements
from servicefoundry.sfy_magic_init_pack.magic_pack import MagicPack
from servicefoundry.sfy_magic_init_pack.util import get_module_name_from_python_file

main_file_content = """
from inspect import signature, getmembers, isfunction
import gradio as gr
try:
    import ${module_name} as functions
except ImportError as error:
    print("Failed to import function ${module_name}: " + str(error))
    raise error


def get_input(param_name, annotation):
    if annotation is None:
        return gr.Textbox(label=param_name)
    elif annotation in [int, float]:
        return gr.Number(label=param_name)
    elif annotation == str:
        return gr.Textbox(label=param_name)
    else:
        raise RuntimeError(f"Unsupported type {annotation}.")


with gr.Blocks() as demo:
    with gr.Tabs():
        for name, func in getmembers(functions, predicate=isfunction):
            with gr.TabItem(name):
                sig = signature(func)
                inputs = []
                for param_name, value in sig.parameters.items():
                    text_input = get_input(param_name, value.annotation)
                    inputs.append(text_input)
                button = gr.Button("Submit")
                output = gr.Textbox(label="Output", interactive=False)
                button.click(func, inputs=inputs, outputs=[output])

demo.launch(server_name="0.0.0.0", server_port=8000)
"""

requirements_txt_content = """
gradio
protobuf==3.20.1
"""


class AutoWebappMagicPack(MagicPack):
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
