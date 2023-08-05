import json
import logging
import os
from functools import wraps
from threading import Lock

import waitress
from flask import (
    Flask,
    Response,
    jsonify,
    make_response,
    request,
    send_file,
    stream_with_context,
)
from werkzeug.serving import run_simple

from . import auto_fetch, auto_sequences, deploy_state, parse_config

app = Flask(__name__)


def serve(config: str, host: str, port: int):
    """
    Start the webserver and background thread
    """
    local_config = parse_config.parse(config, host, port)
    app.config["deploy_root"] = local_config.get("paths", "deploy_root")
    app.config["cache_root"] = local_config.get("paths", "cache_root")
    app.config["auth_token"] = local_config.get("auth", "token")
    app.config["shared_lock"] = Lock()
    app.config["shared_progress_dict"] = {}
    app.config["keep_on_disk"] = 0
    app.config["auto_fetch_event"] = None
    if local_config.getboolean("auto_delete", "on"):
        app.config["keep_on_disk"] = local_config.getint("auto_delete", "keep_on_disk")

    app.logger.info("deploy_root: %s", app.config["deploy_root"])
    app.logger.info("cache_root: %s", app.config["cache_root"])
    app.logger.info("keep_on_disk: %d", app.config["keep_on_disk"])

    host = local_config.get("server", "host")
    port = local_config.getint("server", "port")
    debug = local_config.getint("server", "debug")

    ssl_on = local_config.getboolean("server", "ssl_on")
    ssl_certificate = local_config.get("server", "ssl_certificate")
    ssl_certificate_key = local_config.get("server", "ssl_certificate_key")

    ssl_context = None
    if ssl_on:
        ssl_context = (ssl_certificate, ssl_certificate_key)

    if local_config.getboolean("auto_fetch", "on"):
        if not debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            auto_fetch.run_in_background(app, local_config)

    if local_config.getboolean("server", "on"):

        if debug == 0:
            if ssl_on:
                run_simple(
                    host,
                    port,
                    app,
                    use_reloader=False,
                    use_debugger=False,
                    threaded=True,
                    ssl_context=ssl_context,
                )
            else:
                logger = logging.getLogger("waitress")
                logger.setLevel(logging.INFO)
                waitress.serve(app, host=host, port=port)
        else:
            app.run(debug=True, host=host, port=port, ssl_context=ssl_context)


def require_token(f):
    """
    A decorator to check for a valid token
    """

    @wraps(f)
    def verify_token(*args, **kwargs):
        if not request.headers.get("token") == app.config["auth_token"]:
            return make_response(
                jsonify({"result": "Invalid token", "result_code": 3}), 401
            )
        return f(*args, **kwargs)

    return verify_token


@app.route("/api/v1/test", methods=["GET"])
@require_token
def get_test():
    return jsonify({"result": "It works", "result_code": 0})


@app.route("/api/v1/progress", methods=["GET"])
@require_token
def get_progress():
    with app.config["shared_lock"]:
        progress = app.config["shared_progress_dict"].copy()
    try:
        progress_as_json = jsonify(progress)
    except Exception as err:
        progress_as_json = jsonify({"result": "Internal Error", "result_code": 4})
    return progress_as_json


@app.route("/api/v1/state", methods=["GET"])
@require_token
def get_state():
    with app.config["shared_lock"]:
        state_config, *_ = deploy_state.get_config(app.config["deploy_root"])
    try:
        state = {
            section: state_config[section].get("source_hash")
            for section in state_config.sections()
        }
        state_as_json = jsonify(state)
    except Exception as err:
        state_as_json = make_response(
            jsonify({"result": f"Internal Error {repr(err)}", "result_code": 5}), 500
        )
    return state_as_json


@app.route("/api/v1/state/<root>", methods=["GET"])
@require_token
def get_state_item(root):
    with app.config["shared_lock"]:
        state_config, *_ = deploy_state.get_config(app.config["deploy_root"])
    try:
        state = {root: state_config[root].get("source_hash")}
        state_as_json = jsonify(state)
    except Exception as err:
        state_as_json = make_response(
            jsonify({"result": f"Internal Error {repr(err)}", "result_code": 5}), 500
        )
    return state_as_json


@app.route("/api/v1/trigger/fetch", methods=["GET"])
@require_token
def trigger_fetch():
    with app.config["shared_lock"]:
        auto_fetch_event = app.config["auto_fetch_event"]
    try:
        if auto_fetch_event:
            auto_fetch_event.set_fetch()
            res_as_json = jsonify({"result": "OK", "result_code": 0})
        else:
            res_as_json = jsonify(
                {"result": "auto_fetch is not available", "result_code": 1}
            )
    except Exception as err:
        res_as_json = make_response(
            jsonify({"result": f"Internal Error {repr(err)}", "result_code": 5}), 500
        )
    return res_as_json


@app.route("/api/v1/download/zip/<root>", methods=["GET"])
@require_token
def download_zip(root: str):
    with app.config["shared_lock"]:
        state_config, *_ = deploy_state.get_config(app.config["deploy_root"])
    try:
        zip_file = state_config[root].get("source_file")
        return send_file(zip_file, as_attachment=True)
    except Exception as err:
        return make_response(
            jsonify({"result": f"Internal Error {repr(err)}", "result_code": 5}), 500
        )


@app.route("/api/v1/upload/zip", methods=["POST"])
@require_token
def upload_zip():
    return Response(
        stream_with_context(handle_zip_as_stream(store_data=True, unpack_data=False)),
        content_type="application/json",
    )


@app.route("/api/v1/deploy/zip", methods=["POST"])
@require_token
def post_deploy_zip():
    return Response(
        stream_with_context(handle_zip_as_stream(store_data=True, unpack_data=True)),
        content_type="application/json",
    )


@app.route("/api/v1/deploy/zip", methods=["GET"])
@require_token
def get_deploy_zip():
    return Response(
        stream_with_context(handle_zip_as_stream(store_data=False, unpack_data=True)),
        content_type="application/json",
    )


def handle_zip_as_stream(store_data: bool, unpack_data: bool):
    """
    Stream the progress back to client. The result is formatted as json
    but progress and logging data is not valid json. If client ignores
    lines prefixed with // the result should be valid json
    """

    progress = None
    _handle_zip = auto_sequences.handle_zip(app, request, store_data, unpack_data)

    res = next(_handle_zip)

    if isinstance(res, dict) and "root" in res and res["root"]:
        with app.config["shared_lock"]:
            progress = app.config["shared_progress_dict"][res["root"]] = {}
            log = progress["log"] = []
    else:
        yield f"// {res}\n"

    for res in _handle_zip:
        if isinstance(res, dict):
            if "result" in res:
                yield f"{json.dumps(res)}\n"
            with app.config["shared_lock"]:
                if progress:
                    progress.update(res)
        else:
            yield f"// {res}\n"
            with app.config["shared_lock"]:
                if progress:
                    log.append(res)
