import datetime
import logging
import subprocess

import requests

from servicefoundry.lib.const import ENTITY_JSON_DATETIME_FORMAT
from servicefoundry.lib.exceptions import BadRequestException

logger = logging.getLogger()


def upload_package_to_s3(metadata, package_file):
    with open(package_file, "rb") as file_to_upload:
        http_response = requests.put(metadata["url"], data=file_to_upload)

        if http_response.status_code not in [204, 201, 200]:
            raise RuntimeError(f"Failed to upload to S3 {http_response.content}")


def request_handling(res):
    try:
        status_code = res.status_code
    except Exception:
        raise Exception("Unknown error occurred. Couldn't get status code.")
    if 200 <= status_code <= 299:
        if res.content == b"":
            return None
        return res.json()
    if 400 <= status_code <= 499:
        try:
            message = res.json()["message"]
        except Exception:
            message = res
        raise BadRequestException(res.status_code, message)
    if 500 <= status_code <= 599:
        raise Exception(res.content)


def run_process(cmd, cwd=None):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
    )


def execute(cmd, cwd=None):
    popen = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1,
        cwd=cwd,
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    for stderr_line in iter(popen.stderr.readline, ""):
        yield stderr_line
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, " ".join(cmd))


def json_default_encoder(o):
    if isinstance(o, datetime.datetime):
        return o.strftime(ENTITY_JSON_DATETIME_FORMAT)
