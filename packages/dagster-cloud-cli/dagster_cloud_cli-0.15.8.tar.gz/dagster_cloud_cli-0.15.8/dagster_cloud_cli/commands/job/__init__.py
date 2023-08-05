# pylint: disable=unused-argument


import json
from typing import Any, Dict

import typer
from typer import Typer

from ... import gql, ui
from ...config_utils import dagster_cloud_options

app = Typer(help="Commands for working with Dagster Cloud jobs.")


@app.command(name="launch")
@dagster_cloud_options(allow_empty=True, requires_url=True)
def launch(
    api_token: str,
    url: str,
    location: str = typer.Option(..., "-l", "--location", help="Location name in the deployment."),
    repository: str = typer.Option(
        ..., "-r", "--repository", help="Repository in the specified code location."
    ),
    job: str = typer.Option(..., "-j", "--job", help="Job name to run."),
    tags: str = typer.Option(None, "--tags", help="JSON dict of tags to use for this job run."),
    config: str = typer.Option(
        None, "--config-json", help="JSON string of run config to use for this job run"
    ),
):
    """
    Set the Dagster Cloud deployment settings from a YAML file.
    """
    loaded_tags: Dict[str, Any] = json.loads(tags) if tags else {}
    loaded_config: Dict[str, Any] = json.loads(config) if config else {}

    with gql.graphql_client_from_url(url, api_token) as client:
        ui.print(gql.launch_run(client, location, repository, job, loaded_tags, loaded_config))
