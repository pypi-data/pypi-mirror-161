# https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook


def is_notebook():
    try:
        # noinspection PyUnresolvedReferences
        shell = get_ipython().__class__
        if shell.__name__ == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
        elif shell.__name__ == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        elif "google.colab" in str(shell):
            return True  # google colab notebook
        else:
            return False  # Other type (?)
    except NameError:
        return False  # Probably standard Python interpreter


def get_default_callback():
    if is_notebook():
        from servicefoundry.core.notebook.io.notebook_callback import (
            NotebookOutputCallBack,
        )

        return NotebookOutputCallBack()
    else:
        from servicefoundry.io.output_callback import OutputCallBack

        return OutputCallBack()
