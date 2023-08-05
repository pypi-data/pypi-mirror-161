import json
import pathlib
import re
import shutil
import time
from hashlib import sha256


def store(
    bin_data, cache_root: str, headers: dict, remote_info: dict
):  # -> tuple[pathlib.Path, str]:
    """
    Store the received payload to disk and add a json-file with meta-data.
    """
    if len(bin_data) == 0:
        raise ValueError("Missing post data")
    cache = sha256(bin_data).hexdigest()
    tmp = pathlib.Path.cwd().joinpath(cache_root, cache)
    tmp.mkdir(parents=True, exist_ok=True)
    metadata = {
        "sha256": cache,
        "request_headers": headers,
        "content_len": len(bin_data),
        "remote_info": remote_info,
    }
    post_metadata = tmp.joinpath("post_metadata.json")
    post_metadata.write_text(json.dumps(metadata, indent=2))
    post_data = tmp.joinpath("post_data.zip")
    post_data.write_bytes(bin_data)
    auto_delete = tmp.joinpath("auto_delete.json")
    auto_delete.write_text(
        json.dumps({"root": headers["Root"], "auto_delete": 1, "serial": time.time()})
    )
    return post_data, cache


def find_file_from_headers(
    cache_root: str, headers: dict
):  # -> tuple[pathlib.Path, str]:
    """
    Find a pre stored zip file using the Zip-Sha256 header from request object
    """
    cache = headers.get("Zip-Sha256", "")
    if not cache:
        raise ValueError("header Zip-Sha256 is missing")
    if not re.search(r"\W", cache) is None:
        raise ValueError("header Zip-Sha256 is not sha256")
    if not len(cache) == 64:
        raise ValueError("header Zip-Sha256 is not sha256")

    tmp = pathlib.Path.cwd().joinpath(cache_root, cache, "post_data.zip")
    if not tmp.exists():
        raise ValueError("file not found")
    return tmp, cache


def auto_delete(cache_root: str, keep_on_disk: int, handle_root=""):
    """
    Delete old cache dirs and its content.
    """
    tmp = pathlib.Path.cwd().joinpath(cache_root)
    file_list = tmp.glob("*/auto_delete.json")
    root_mapping = {}

    for file in file_list:
        info = json.loads(file.read_text())
        if info["auto_delete"] == 1:
            root = info["root"]
            serial = info["serial"]
            if not root in root_mapping:
                root_mapping[root] = {}
            root_mapping[root][serial] = file.parent

    for root, serial_mapping in root_mapping.items():
        if handle_root and not handle_root == root:
            continue
        for serial in sorted(serial_mapping.keys(), reverse=True)[keep_on_disk:]:
            path = serial_mapping[serial]
            yield f"auto remove expired cache {path.name}"
            print(f"auto remove expired cache {path}")
            shutil.rmtree(path, ignore_errors=True)
