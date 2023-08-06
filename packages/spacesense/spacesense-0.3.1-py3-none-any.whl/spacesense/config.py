import json
import logging

import pkg_resources

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s : %(message)s")

_CONFIG = json.load(pkg_resources.resource_stream(__name__, "resources/config.json"))

with open(pkg_resources.resource_filename(__name__, "resources/server.crt"), "rb") as fh:
    CERT = fh.read()

DEBUG = _CONFIG["debug"]
GRPC_MAX_SEND_MESSAGE_LENGTH = 512 * 1024 * 1024
GRPC_MAX_RECEIVE_MESSAGE_LENGTH = 512 * 1024 * 1024
BACKEND_URL = "platform-api.spacesense.ai:8000"
