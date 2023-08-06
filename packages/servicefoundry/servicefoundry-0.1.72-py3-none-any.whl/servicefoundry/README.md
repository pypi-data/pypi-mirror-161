## Note
* The code is divided into modules. Before making changes read the intended use of modules.
* Don't create cross dependency between build pack.
Keep all the common logic in `sfy_build_pack_common`
* Don't use __init__.py except for client facing API's. IDE doesn't do a good job of refactoring these.

## io

This module contains input and output interface. These interface has no cli or notebook specific logic.
cli.io module has cli specific implementation. core.notebook.io has notebook related implementation.

## lib

This module contains dao for cluster, workspace, service, deployment.
Keep this module free from cli or notebook specific logic.

## sfy_build

This module is executed when `sfy build` is executed.
This module take care of converting code to docker image.

This package runs all the build_pack in a chain.
New build pack can be added in chain at [build_pack.py](sfy_build/build_pack.py)

All the build pack must have `detect.py` and `build.py`.

Example `build.py`:
```python
def build(name, build_dir, **kwargs):
    pass
```

Example `detect.py`:
```python
def detect(**kwargs):
    pass
```


## sfy_build_pack_common

This module has utilities which is used by build packs.

## sfy_build_pack_docker

This build pack will build if there is Dockerfile

## sfy_build_pack_python

This build pack will build if there is `requirements.txt` and `Procfile`

## sfy_build_pack_fallback

This build pack will try building everything else using 3rd party build packs.
