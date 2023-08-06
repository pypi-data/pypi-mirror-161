import os
from urllib import parse

QUEUE_APP_ID = "app_queue_client"


def prepare_queue_central_url(username, password):
    if username is None or password is None:
        raise RuntimeError(
            "username or password must be provided if using queue"
        )
    hostname = os.environ.get(
        "UTF_QUEUE_HOSTNAME", "utf-queue-central.silabs.net"
    )
    scheme = os.environ.get("UTF_QUEUE_SCHEME", "amqps")
    port = os.environ.get("UTF_QUEUE_PORT", "443")
    virtual_host = os.environ.get("UTF_QUEUE_VIRTUAL_HOST", "%2f")
    return f"{scheme}://{username}:{parse.quote(password)}@{hostname}:{port}/{virtual_host}"