import re

def verify_content(header_content_len: int, received_data_len: int, file_len: int):
    """
    Make sure that received data length matches request content length.
    """

    yield "verify data"
    if file_len != received_data_len:
        raise ValueError(
            f"file_len {file_len} and received_data_len {received_data_len} differs"
        )
    if file_len != header_content_len:
        raise ValueError(
            f"file_len {file_len} and Content-Length {header_content_len} differs"
        )


def verify_root(root_dir_name: str, headers: dict):
    """
    Make sure Root key from header matches the root dir from zip file
    """
    yield "verify root dir"
    root_from_header = headers.get("Root", "")
    if not (root_dir_name.lower() == root_from_header.lower()):
        raise ValueError(
            f" zip root dir: {root_dir_name} and header Root: {root_from_header} differs"
        )
    if not verify_safe_basename(root_dir_name):
        raise ValueError(
            f" zip root dir: found illegal characters"
        )


def verify_safe_basename(text):
    # remove reserved windows keywords
    reserved_win_keywords = r"(PRN|AUX|CLOCK\$|NUL|CON|COM[1-9]|LPT[1-9])"

    # remove reserved windows characters
    reserved_win_chars = '[\x00-\x1f\\\\?*:";|/<>]'
    # reserved posix is included in reserved_win_chars. reserved_posix_characters = '/\0'

    extra_chars = "[%$@{}]"

    if not text:
        return False

    return re.search(f"{reserved_win_keywords}|{reserved_win_chars}|{extra_chars}", text) is None
