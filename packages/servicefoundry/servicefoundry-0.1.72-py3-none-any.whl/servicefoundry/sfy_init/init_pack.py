import importlib
from typing import Dict

from servicefoundry.sfy_init.pack import Pack


def _load_init_pack(module_name: str, clazz: str):
    try:
        detect_module = getattr(importlib.import_module(module_name), clazz)
        return detect_module()
    except Exception as e:
        print(f"Failed to load {module_name} because of exception: {str(e)}")
        return None


init_packs_modules = [
    ("servicefoundry.sfy_init_packs.fastapi_pack", "FastApiPack"),
    ("servicefoundry.sfy_init_packs.gradio_pack", "GradioPack"),
    ("servicefoundry.sfy_init_packs.tensorflow_serving_pack", "TfServePack"),
]


def get_init_pack():
    res: Dict[Pack, str] = {}
    for pack_module, pack_clazz in init_packs_modules:
        pack: Pack = _load_init_pack(pack_module, pack_clazz)
        if pack:
            res[pack] = pack.get_description()
    return res
