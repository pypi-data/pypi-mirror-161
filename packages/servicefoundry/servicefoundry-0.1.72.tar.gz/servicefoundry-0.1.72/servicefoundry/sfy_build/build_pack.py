import importlib

from servicefoundry.io.output_callback import OutputCallBack
from servicefoundry.lib.exceptions import ConfigurationException


class BuildPack:
    def __init__(self, name, detect, build):
        self.name = name
        self._detect = detect
        self._build = build

    def detect(self):
        return self._detect()

    def build(
        self, name, build_dir, options, output_hook: OutputCallBack, cache: str = None
    ):
        return self._build(
            name=name,
            build_dir=build_dir,
            options=options,
            output_hook=output_hook,
            cache=cache,
        )


# Build pack are loaded dynamically so that bug in one build pack does not affect others.
def _get_build_pack(module_name):
    def _build_pack():
        try:
            detect_module = importlib.import_module(f"{module_name}.detect")
            build_module = importlib.import_module(f"{module_name}.build")
            return BuildPack(module_name, detect_module.detect, build_module.build)
        except Exception as e:
            print(f"Failed to load {module_name} because of exception: {str(e)}")
            return None

    return _build_pack


_build_pack_provider_chain = {
    "sfy_build_pack_docker": _get_build_pack("servicefoundry.sfy_build_pack_docker"),
    "sfy_build_pack_python": _get_build_pack("servicefoundry.sfy_build_pack_python"),
    "sfy_build_pack_fallback": _get_build_pack(
        "servicefoundry.sfy_build_pack_fallback"
    ),
}


def get_build_pack(name: str):
    if name not in _build_pack_provider_chain:
        raise ConfigurationException(
            f"Couldn't find build pack {name}. "
            f"Valid choices are {','.join(_build_pack_provider_chain.keys())}"
        )
    return _build_pack_provider_chain[name]()


def detect_build_pack():
    final_build_pack = None
    for build_pack_provider in _build_pack_provider_chain.values():
        build_pack = build_pack_provider()
        if build_pack is not None and build_pack.detect() and final_build_pack is None:
            final_build_pack = build_pack
    return final_build_pack
