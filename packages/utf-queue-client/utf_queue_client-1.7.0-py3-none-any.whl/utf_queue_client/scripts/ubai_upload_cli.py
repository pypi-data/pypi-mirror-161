import json
from utf_queue_client.clients.ubai_artifact_upload_request_producer import (
    UbaiArtifactUploadRequestProducer,
)
from ubai_client.apis import ArtifactApi
import click
from typing import Iterable, Tuple
from time import sleep
from utf_queue_client.scripts import setup_telemetry, get_or_make_ca_file
from retry import retry
import requests
from otel_extensions import instrumented
from opentelemetry import trace

from utf_queue_client.utils import prepare_queue_central_url

MULTIPART_SIZE_THRESHOLD = 1000000


@click.command()
@click.option(
    "--file-path",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to file to upload",
)
@click.option("--metadata", multiple=True, type=(str, str))
@click.option(
    "--username",
    envvar="UTF_QUEUE_USERNAME",
    help="UTF queue username",
)
@click.option(
    "--password",
    envvar="UTF_QUEUE_PASSWORD",
    help="UTF queue password",
)
@click.option(
    "--client-id", type=str, default="Unknown Client", help="Optional client identifier"
)
@click.option(
    "--retries", default=6, help="number of retries (in case of network-related issues)"
)
@click.option("--queue/--no-queue", default=False)
def cli_entrypoint(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int,
    queue: bool,
):
    cli(file_path, metadata, username, password, client_id, retries, queue)


def cli(
    file_path: str,
    metadata: Iterable[Tuple[str, str]],
    username: str,
    password: str,
    client_id: str,
    retries: int = 6,
    queue: bool = False,
):
    with setup_telemetry():
        url = ""
        if queue:
            url = prepare_queue_central_url(username, password)

        metadata_dict = {}
        for key, value in metadata:
            metadata_dict[key] = value

        @retry(Exception, delay=3, backoff=2, max_delay=12, tries=retries + 1)
        def retry_wrapper():
            if queue:
                upload_artifact_through_queue(url, client_id, file_path, metadata_dict)
            else:
                upload_artifact_direct(file_path, metadata_dict)

        retry_wrapper()
        if not queue:
            # workaround to reduce load
            sleep(2)


@instrumented
def upload_artifact_through_queue(url, client_id, file_path, metadata_dict):
    client = UbaiArtifactUploadRequestProducer(url, client_id)
    client.upload_artifact(file_path, metadata=metadata_dict)


@instrumented
def upload_artifact_direct(file_path, metadata_dict):
    (
        name,
        extension,
        contents,
        base64_content,
    ) = UbaiArtifactUploadRequestProducer.extract_payload(file_path)
    span = trace.get_current_span()
    span.set_attribute("artifact.name", name)
    span.set_attribute("artifact.extension", extension)
    span.set_attribute("artifact.length", len(contents))
    for key in metadata_dict:
        span.set_attribute(f"metadata.{key}", metadata_dict[key])
    if len(contents) > MULTIPART_SIZE_THRESHOLD:
        span.set_attribute("multipart_upload", True)
        # use multipart transfer endpoint
        artifact_api = ArtifactApi()
        with open(file_path, "rb") as f:
            files = {"file": (name + extension, f)}
            resp = requests.post(
                f"{artifact_api.api_client.configuration.host}/api/v1/artifact-upload-file",
                files=files,
                data={"metadata": json.dumps(metadata_dict)},
                verify=get_or_make_ca_file()
            )
            if resp.status_code != 200 and resp.status_code != 201:
                raise RuntimeError(resp.content)
    else:
        span.set_attribute("multipart_upload", False)
        UbaiArtifactUploadRequestProducer.upload_artifact_direct(
            name, extension, base64_content, metadata_dict
        )


if __name__ == "__main__":
    cli_entrypoint()
