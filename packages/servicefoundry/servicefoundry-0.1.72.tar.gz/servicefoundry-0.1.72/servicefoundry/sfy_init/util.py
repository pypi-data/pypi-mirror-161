import shutil
from datetime import datetime

from servicefoundry.io.input_hook import InputHook
from servicefoundry.io.output_callback import OutputCallBack


def _maybe_backup_file(file_path, input_hook: InputHook, output_hook: OutputCallBack):
    if file_path.exists():
        overwrite = input_hook.confirm(
            prompt=f"File {str(file_path)!r} already exists, Overwrite?",
            default=False,
        )
        if not overwrite:
            raise Exception("Aborted by user!")
        else:
            _now = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
            destination_path = str(
                file_path.parent / f"{file_path.stem}-{_now}-backup.yaml"
            )
            shutil.copy2(
                src=file_path,
                dst=destination_path,
            )
            output_hook.print_line(
                f"Your current config was backed up to {destination_path!r}"
            )
