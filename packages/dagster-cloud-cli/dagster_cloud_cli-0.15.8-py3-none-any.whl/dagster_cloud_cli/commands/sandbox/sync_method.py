import subprocess
from abc import abstractmethod
from enum import Enum
from queue import Empty, Queue
from threading import Thread
from typing import Dict, Iterable, NamedTuple, Optional, Tuple

from ... import ui
from .utils import get_current_display_timestamp


class SandboxConnectionInfo(
    NamedTuple(
        "_SandboxConnectionInfo",
        [
            ("username", str),
            ("hostname", str),
            ("port", int),
        ],
    )
):
    def __new__(cls, username: str, hostname: str, port: int):
        return super(SandboxConnectionInfo, cls).__new__(cls, username, hostname, port)


class SyncedDirectory(NamedTuple):
    identifier: str
    location_name: str
    connection_info: SandboxConnectionInfo
    from_directory: str
    to_directory: str


class SyncStatus(Enum):
    SYNCED = "SYNCED"
    SYNCING = "SYNCING"
    UNAVAILABLE = "ERRORED"


class SyncMethod:
    @abstractmethod
    def preflight(self, verbosity_level: int) -> None:
        """
        Validates that this sync method is available.
        """

    @abstractmethod
    def create_directory_sync(
        self,
        information: SyncedDirectory,
    ) -> None:
        """
        Set up a directory to be synced.
        """

    @abstractmethod
    def sync_loop(
        self, timeout: Optional[float] = None
    ) -> Iterable[Optional[Tuple[str, SyncStatus]]]:
        """
        Synchronize all set up directories. This method should run until interrupted,
        yielding an (identifier, SyncState) tuple when a state change is detected.

        For active sync methods managed by the CLI, this loop may actually conduct the
        synchronization process. For methods managed externally, such as Mutagen, this
        loop is only responsible for monitoring the state of the synchronization process.

        Can also specify a timeout, after which the sync loop should yield None.
        """

    @abstractmethod
    def cleanup_directory_sync(self, identifier: str) -> None:
        """
        Stop and clean up any information associated with a synced directory.
        """


class MutagenSyncMethod(SyncMethod):
    """
    Synchronization method which relies on the Mutagen CLI to transport
    files between the source and destination over SSH.
    """

    def __init__(self):
        self.targets: Dict[str, SyncedDirectory] = {}
        self.monitor_threads: Dict[str, Thread] = {}
        self.verbosity_level: int = 0
        self.syncing = False
        self.console_out_queue: Optional[Queue] = None

    def preflight(self, verbosity_level: int) -> None:
        try:
            subprocess.check_output(["mutagen", "version"])
        except subprocess.CalledProcessError:
            raise ui.error(
                f"{ui.as_code('mutagen')} executable not found. You must install mutagen "
                f"in order to use code syncing functionality.\n\nRun {ui.as_code('brew install mutagen-io/mutagen/mutagen')} "
                f"or see {ui.as_code('https://mutagen.io/documentation/introduction/installation')}."
            )
        self.verbosity_level = verbosity_level

    def create_directory_sync(
        self,
        information: SyncedDirectory,
    ) -> None:
        subprocess.check_output(
            [
                "mutagen",
                "sync",
                "create",
                information.from_directory,
                (
                    f"{information.connection_info.username}@{information.connection_info.hostname}"
                    f":{information.connection_info.port}:{information.to_directory}"
                ),
                f"--name={information.identifier}",
                "--sync-mode",
                "one-way-replica",
                "--watch-mode-beta=no-watch",
                # Start sessions paused so we get all lifecycle events
                # unpause during sync loop
                "--paused",
            ]
        )
        self.targets[information.identifier] = information

        if self.syncing:
            self.setup_sync_thread(information.identifier)

    def setup_sync_thread(self, identifier: str) -> None:
        """
        Sets up a thread to monitor the mutagen state for this identifier,
        then resumes the sync process.

        Standard out is forwarded to the console out queue.
        """

        assert self.syncing
        assert self.console_out_queue

        def pass_console_output(identifier, out, queue):
            for stdout_line in iter(out.readline, ""):
                queue.put((identifier, stdout_line))
            out.close()

        popen = subprocess.Popen(
            ["mutagen", "sync", "monitor", identifier],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL if self.verbosity_level == 0 else None,
            universal_newlines=True,
            bufsize=1,
        )
        t = Thread(
            target=pass_console_output, args=(identifier, popen.stdout, self.console_out_queue)
        )
        t.daemon = True
        t.start()
        self.monitor_threads[identifier] = t
        subprocess.check_output(["mutagen", "sync", "resume", identifier])

    def sync_loop(
        self, timeout: Optional[float] = None
    ) -> Iterable[Optional[Tuple[str, SyncStatus]]]:
        self.syncing = True
        try:
            # https://stackoverflow.com/a/4896288

            self.console_out_queue = Queue()
            for identifier in self.targets:
                self.setup_sync_thread(identifier)
            while True:
                try:
                    identifier, stdout_line = self.console_out_queue.get(timeout=timeout)

                    if self.verbosity_level >= 2:
                        print(
                            f"[{get_current_display_timestamp()}] [mutagen] {stdout_line.strip()}"
                        )

                    # List of states:
                    # https://github.com/mutagen-io/mutagen/blob/master/pkg/synchronization/state.proto
                    if (
                        "Applying" in stdout_line
                        or "Staging" in stdout_line
                        or "Reconciling" in stdout_line
                    ):
                        yield (identifier, SyncStatus.SYNCING)

                    elif "Saving archive" in stdout_line:
                        yield (identifier, SyncStatus.SYNCED)

                    elif "Errored" in stdout_line:
                        yield (identifier, SyncStatus.UNAVAILABLE)
                except Empty:
                    yield None
        finally:
            self.syncing = False

    def cleanup_directory_sync(self, identifier: str) -> None:
        subprocess.check_output(["mutagen", "sync", "terminate", identifier])
        del self.targets[identifier]
        if identifier in self.monitor_threads:
            self.monitor_threads[identifier].join()
            del self.monitor_threads[identifier]
