# pylint: disable=unused-argument

import os
import re
import subprocess
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List, Optional

import typer
import yaml
from dagster_cloud_cli.commands.sandbox.utils import get_current_display_timestamp
from typer import Typer

from ... import gql, ui
from ...config_utils import dagster_cloud_options
from ...core.graphql_client import GqlShimClient
from .sync_method import (
    MutagenSyncMethod,
    SandboxConnectionInfo,
    SyncMethod,
    SyncStatus,
    SyncedDirectory,
)
from .utils import get_current_display_timestamp

CONNECTION_INFO_GIVE_UP_TIME = timedelta(seconds=120)

app = Typer(help="Interface with your dev sandbox.")


def get_all_connection_info(client: GqlShimClient) -> Dict[str, SandboxConnectionInfo]:
    """
    Returns a mapping of location name to sandbox connection info for all locations.
    """
    workspace_entries = gql.fetch_workspace_entries(client)
    return {
        workspace_entry["locationName"]: SandboxConnectionInfo(
            username=workspace_entry["connectionInfo"]["username"],
            hostname=workspace_entry["connectionInfo"]["hostname"],
            port=workspace_entry["connectionInfo"]["port"],
        )
        for workspace_entry in workspace_entries
        if workspace_entry.get("connectionInfo")
    }


def launch_ssh(arguments: List[str]) -> None:
    os.execvp("ssh", ["ssh", *arguments])


def get_default_sync_method() -> SyncMethod:
    return MutagenSyncMethod()


@contextmanager
def dev_deployment_client_or_error(
    base_client_url: str, organization: str, api_token: str
) -> Generator[GqlShimClient, None, None]:
    with gql.graphql_client_from_url(base_client_url, api_token) as default_client:
        try:
            dev_depl = gql.get_dev_deployment_name(default_client)
        except Exception:
            raise ui.error(
                "No dev sandbox found for your user - you need to set one up before you can use this command."
            )
        # Current deployment is dev depl
        if not dev_depl:
            yield default_client

        # Else, construct new gql client
    with gql.graphql_client_from_url(
        gql.url_from_config(organization, dev_depl), api_token
    ) as new_client:
        yield new_client


@app.command(name="ssh")
@dagster_cloud_options(requires_url=True)
def ssh(
    organization: str,
    deployment: str,
    api_token: str,
    url: str,
    location_name=typer.Argument(
        ..., help="The name of the code location whose user code server to connect to."
    ),
) -> None:
    """
    Connects to the user code server hosting a given code location.
    """
    with dev_deployment_client_or_error(url, organization, api_token) as client:
        all_connection_info = get_all_connection_info(client)

        if not location_name in all_connection_info:
            raise ui.error(f"Cannot find sandbox user code server for location {location_name}.")

        connection_info = all_connection_info[location_name]

        # TODO forward all other arguments to SSH
        launch_ssh(
            [
                "-p",
                str(connection_info.port),
                f"{connection_info.username}@{connection_info.hostname}",
            ]
        )


def find_locations_yaml(search_directory: str) -> Optional[str]:
    """
    Given a search directory, finds a locations.yaml file located
    in the search directory or a parent. Returns None if none is found.
    """
    curr_dir = search_directory

    while not os.path.exists(os.path.join(curr_dir, "locations.yaml")):
        parent_dir = os.path.dirname(curr_dir)
        if parent_dir == curr_dir:
            return None
        curr_dir = parent_dir
    return curr_dir


def get_directory_identifier(location_name: str, index: int) -> str:
    return f"{re.sub('[^0-9a-zA-Z-]+', '-', location_name)}-{index}"


def get_directories_to_sync(
    directory: str,
    all_connection_info: Dict[str, SandboxConnectionInfo],
    show_errors: bool = True,
) -> Dict[str, SyncedDirectory]:
    """
    Finds a set of code sync mappings defined in a locations.yaml file,
    combines with the sandbox connection info to create a list of directories to sync.
    """
    locations_yaml_dir = find_locations_yaml(directory)
    if not locations_yaml_dir:
        raise ValueError("No locations.yaml file found")

    directories_to_sync: Dict[str, SyncedDirectory] = {}
    with open(os.path.join(locations_yaml_dir, "locations.yaml"), encoding="utf8") as f:
        locations = yaml.safe_load(f.read())["locations"]

        defined_locations = set(locations.keys())
        available_locations = set(all_connection_info.keys())

        if show_errors:
            if len(available_locations.intersection(defined_locations)) == 0:
                defined_locations_display = ", ".join(locations.keys()) or "(None)"
                available_locations_display = ", ".join(all_connection_info.keys()) or "(None)"
                raise ui.error(
                    "No accessable sync locations found\n\n"
                    f"Defined in locations.yaml: {defined_locations_display}\nAvailable code locations: {available_locations_display}"
                )

            if len(defined_locations - available_locations) > 0:
                not_synced = ", ".join(defined_locations - available_locations)
                ui.warn(
                    f"Some locations defined in locations.yaml are not accessible to sync: {not_synced}\n"
                )

            if len(available_locations - defined_locations) > 0:
                not_synced = ", ".join(available_locations - defined_locations)
                ui.warn(
                    f"Some available locations are not defined in locations.yaml, and will not be synced: {not_synced}\n"
                )

        for location_name, location in locations.items():
            if location_name in all_connection_info:
                connection_info = all_connection_info[location_name]
                for i, mapping in enumerate(location.get("code_sync", [])):
                    ident = get_directory_identifier(location_name, i)
                    directories_to_sync[ident] = SyncedDirectory(
                        identifier=ident,
                        location_name=location_name,
                        from_directory=str(os.path.join(locations_yaml_dir, mapping.get("from"))),
                        to_directory=mapping.get("to"),
                        connection_info=connection_info,
                    )
    return directories_to_sync


def validate_host_connection(
    connection_info: SandboxConnectionInfo,
    automatically_add_keys: bool = True,
) -> bool:
    """
    Validates that we can SSH into the given host, and prompts the user to add to
    known_hosts if need be.
    """
    return (
        subprocess.call(
            [
                "ssh",
                "-p",
                f"{connection_info.port}",
                "-o",
                "ConnectTimeout=10",
                *(["-o", "StrictHostKeyChecking=accept-new"] if automatically_add_keys else []),
                f"{connection_info.username}@{connection_info.hostname}",
                "exit",
            ],
            stdout=subprocess.DEVNULL if automatically_add_keys else None,
            stderr=subprocess.DEVNULL if automatically_add_keys else None,
        )
        == False
    )


def print_sync_state(
    state_map: Dict[str, SyncStatus], remove_previous: bool = True, refetching: bool = False
):
    """
    Given a mapping from directory identifiers to sync states, prints a summary of
    all sync states.
    """
    if remove_previous:
        ui.erase_previous_line(2)

    c = Counter(state_map.values())
    n_unavailable = c.get(SyncStatus.UNAVAILABLE, 0)
    n_syncing = c.get(SyncStatus.SYNCING, 0)
    n_synced = c.get(SyncStatus.SYNCED, 0)
    total = len(state_map.keys()) - n_unavailable

    if n_syncing > 0:
        ui.print(
            ui.yellow(
                f"[{get_current_display_timestamp()}] ({n_synced}/{total}) Syncing directories..."
            )
        )
    else:
        ui.print(ui.blue(f"[{get_current_display_timestamp()}] ({n_synced}/{total}) Sync complete"))

    if n_unavailable > 0:
        refetch_text = ", trying to reconnect" if refetching else ""
        ui.print(ui.red(f"           {n_unavailable} directories unable to sync{refetch_text}"))
    elif remove_previous:
        ui.print()


def fetch_directories_to_sync(
    client: GqlShimClient, automatically_add_keys: bool, show_errors=False
) -> Dict[str, SyncedDirectory]:
    all_connection_info = get_all_connection_info(client)
    for connection_info in all_connection_info.values():
        if not validate_host_connection(
            connection_info, automatically_add_keys=automatically_add_keys
        ):
            raise ui.error("Unable to establish connection")

    return get_directories_to_sync(
        os.path.abspath(os.getcwd()), all_connection_info, show_errors=show_errors
    )


@app.command(name="sync")
@dagster_cloud_options(requires_url=True)
def code_sync(
    organization: str,
    deployment: str,
    api_token: str,
    url: str,
    verbose: bool = typer.Option(False, "--verbose", "-v", is_flag=True),
    very_verbose: bool = typer.Option(False, "--very-verbose", "-vv", is_flag=True),
    prompt_host_key: bool = typer.Option(
        False,
        "--prompt-host-key",
        "-p",
        is_flag=True,
        help="Prompt to accept new host key fingerprints.",
    ),
    reconnect_timeout: int = typer.Option(
        10,
        "--reconnect-timeout",
        "-r",
        help="Timeout in seconds before attempting to reconnect to a sandbox location.",
    ),
):
    """
    Starts to synchronize code in the local environment with code in your cloud sandbox.
    """
    if verbose and very_verbose:
        raise ui.error(
            f"Cannot specify both {ui.as_code('--verbose')} and {ui.as_code('--very-verbose')} options"
        )
    verbosity_level = 2 if very_verbose else 1 if verbose else 0

    with dev_deployment_client_or_error(url, organization, api_token) as client:

        sync_method = get_default_sync_method()
        sync_method.preflight(verbosity_level)

        directories_to_sync = fetch_directories_to_sync(
            client, automatically_add_keys=not prompt_host_key
        )

        ui.print("Enabling code sync...")

        for directory in directories_to_sync.values():
            sync_method.create_directory_sync(directory)

        identifier_location_name_map = {
            directory.identifier: directory.location_name
            for directory in directories_to_sync.values()
        }
        try:
            states_map = {ident: SyncStatus.SYNCING for ident, dir in directories_to_sync.items()}
            unavailable_time = None

            print()
            print_sync_state(states_map, remove_previous=True)

            for update in sync_method.sync_loop(timeout=5):
                if update:
                    identifier, new_state = update

                    last_state = states_map[identifier]
                    states_map[identifier] = new_state

                    # If we have just finished syncing, soft reload sandbox location
                    if new_state == SyncStatus.SYNCED and last_state != new_state:
                        gql.reload_repo_location(client, identifier_location_name_map[identifier])

                    # If we have had a meaningful state update, reprint status
                    if (
                        new_state == SyncStatus.SYNCING
                        or new_state == SyncStatus.UNAVAILABLE
                        or last_state != new_state
                    ):
                        print_sync_state(states_map, remove_previous=verbosity_level == 0)

                    # Keep track of how long one or more locations has been unavailable
                    if not unavailable_time and new_state == SyncStatus.UNAVAILABLE:
                        unavailable_time = datetime.now()
                    elif unavailable_time and all(
                        v != SyncStatus.UNAVAILABLE for v in states_map.values()
                    ):
                        unavailable_time = None

                # If we have been unavailable for a while, re-fetch connection info
                # and restart any mutagen syncs that have different connection info
                if unavailable_time and datetime.now() > unavailable_time + timedelta(
                    seconds=reconnect_timeout
                ):
                    print_sync_state(
                        states_map, remove_previous=verbosity_level == 0, refetching=True
                    )
                    new_directories_to_sync = fetch_directories_to_sync(
                        client, automatically_add_keys=not prompt_host_key, show_errors=False
                    )
                    for ident in states_map:
                        if (
                            states_map[ident] == SyncStatus.UNAVAILABLE
                            and ident in new_directories_to_sync
                            and new_directories_to_sync[ident] != directories_to_sync[ident]
                        ):
                            sync_method.cleanup_directory_sync(ident)
                            sync_method.create_directory_sync(new_directories_to_sync[ident])

                    unavailable_time = None

        except KeyboardInterrupt:
            pass
        finally:
            ui.print("Terminating sync...")
            for directory in directories_to_sync.values():
                sync_method.cleanup_directory_sync(directory.identifier)
