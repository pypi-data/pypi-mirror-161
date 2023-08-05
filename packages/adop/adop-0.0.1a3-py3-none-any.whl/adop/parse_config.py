import configparser
import pathlib
import secrets

default_config = """[server]
on = 1
host = 127.0.0.1
port = 8000
debug = 0

ssl_on = 0
ssl_certificate =
ssl_certificate_key =

[paths]
deploy_root = ./work/auto
cache_root = ./work/cache

[auth]
token = 

[auto_delete]
on = 1
keep_on_disk = 5

[auto_fetch]
on = 0
run_at_startup = 1
interval = 7200
sources = github_example, gitlab_example, self_hosted_example
"""

default_example_config = """
[github_example]
root = simple-master
check_url = https://api.github.com/repos/fholmer/simple/git/refs/heads/master
payload_url = https://github.com/fholmer/simple/archive/refs/heads/master.zip

[gitlab_example]
root = simple-master
check_url = https://gitlab.com/api/v4/projects/fholmer%%2Fsimple/repository/branches/master
payload_url = https://gitlab.com/fholmer/simple/-/archive/master/simple-master.zip
headers = User-agent: Mozilla/5.0

[self_hosted_example]
root = simple
check_url = https://example.local/api/v1/state/simple
payload_url = https://example.local/api/v1/download/simple
headers = Token: NO, Host: distribute
"""


class Config:
    """
    Read config file or create one if it does not exist.
    """

    def __init__(self, config_file_path: str, host: str, port: int):
        self.config = configparser.ConfigParser()
        self.config.read_string(default_config)
        config_file = pathlib.Path.cwd().joinpath(config_file_path)
        if not config_file.exists():
            self.config.read_string(default_example_config)
            # auto generate token
            self.config.set("auth", "token", secrets.token_urlsafe(32))
            # ensure that folders exists
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with config_file.open(mode="w") as f:
                self.config.write(f)
        else:
            self.config.read_string(config_file.read_text())

        # if host or port is set from command line arguments these
        # should be used instead of the configured host/port
        if host:
            self.config.set("server", "host", host)
        if port:
            self.config.set("server", "port", str(port))
        # enforce authorization token
        if not self.config.get("auth", "token"):
            raise ValueError("[auth]token missing in config file")


def parse(config_file: str, host: str, port: int) -> configparser.ConfigParser:
    """
    Return a object that holds config info
    """
    config = Config(config_file, host, port)
    return config.config
