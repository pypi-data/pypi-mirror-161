from datetime import datetime
from contextlib import contextmanager
import os
import shutil
from typing import Union
from pathlib import Path
from docker import APIClient
from docker.errors import DockerException
from rich.progress import Progress
from rich.status import Status
from rich.table import Table
from rich.live import Live
import pwinput
from rich.panel import Panel
from rich import box
from rich import print

from ..spawner.lib import load_config
from ..exceptions import GreapDockerError
from ..backtest import collect


class DockerBuilder:
    def __init__(self, root_dir: Union[str, Path]):
        self._root_dir = root_dir
        try:
            self._client = APIClient()
        except DockerException as e:
            raise GreapDockerError("Please check that you have started docker") from e
        self._tag = "latest"
        self._username = None

    @contextmanager
    def _create_docker_file_if_not_exist(self, x86: bool):
        src = Path(__file__).parent / (
            "template.Dockerfile" if x86 else "amd64.Dockerfile"
        )
        dst = Path(self._root_dir) / "Dockerfile"
        try:
            if dst.exists():
                yield
                return
            shutil.copy(src, dst)
            yield
        finally:
            os.remove(dst)

    @contextmanager
    def _create_backtest_db_if_not_exist(self):
        rd = Path(self._root_dir)
        config = load_config(rd)
        symbols = config["fetch"]["symbols"]
        start_at = config["fetch"]["start_at"]
        end_at = datetime.now()
        output_path = rd / "backtest.db"
        if output_path.exists():
            print("Backtest DB already exists. Skip Collecting")
        else:
            print("Backtest DB does not exist. Collect backtest data...")
            collect(symbols, output_path, start_at, end_at)
        yield

    @contextmanager
    def _create_requirements_txt_if_not_exist(self):
        dst = Path(self._root_dir) / "requirements.txt"
        if dst.exists():
            yield
        else:
            dst.touch()
            yield

    @contextmanager
    def _increase_timeout_to(self, timeout=30000):
        old_timeout = os.environ.get("DOCKER_CLIENT_TIMEOUT", "")
        os.environ["DOCKER_CLIENT_TIMEOUT"] = str(timeout)
        yield
        os.environ["DOCKER_CLIENT_TIMEOUT"] = old_timeout

    def login(self):
        user = input("Docker ID: ")
        password = pwinput.pwinput(prompt="Docker Password: ")
        os.system("docker logout >/dev/null 2>&1")
        resp = self._client.login(username=user, password=password)
        print(resp["Status"])
        self._username = user
        return self

    @property
    def repo(self):
        return f"{self._username}/{str(Path(self._root_dir).name)}"

    def _docker_build(self, nocache: bool, platform: str):
        dockerfile = Path(self._root_dir) / "Dockerfile"
        with open(dockerfile, "r") as f:
            steps = len(
                [
                    l
                    for l in f.readlines()
                    if l.strip() and not l.strip().startswith("#")
                ]
            )

        status = Status(status="Build Docker Image")
        progress = Progress()
        task = progress.add_task("[yellow]Build Docker Image...", total=steps)
        table = Table.grid()
        subtable = Table.grid()
        subtable.add_row(
            Panel.fit(status, title="[b]Status"), Panel.fit(progress, box=box.MINIMAL)
        )
        table.add_row(subtable)

        print("nocache", nocache)
        with Live(table):
            for line in self._client.build(
                path=self._root_dir,
                decode=True,
                nocache=nocache,
                platform=platform,
                tag=self.repo,
            ):
                if "stream" in line and "Step" in line["stream"]:
                    progress.advance(task)
                    status.update(line["stream"])
                elif "errorDetail" in line:
                    raise GreapDockerError(line["errorDetail"]["message"])
                elif "stream" in line and line["stream"] != "\n":
                    print(line["stream"])

    def build(self, nocache: bool, x86: bool = True):
        with self._create_backtest_db_if_not_exist():
            with self._create_docker_file_if_not_exist(x86):
                platform = "linux/amd64" if not x86 else None
                self._docker_build(nocache, platform)
        return self

    def push(self):
        status = Status(status="Push Docker Image")
        progress = Progress()
        table = Table.grid()
        table.add_row(
            Panel.fit(status, title="[b]Status"), Panel.fit(progress, box=box.MINIMAL)
        )
        tasks = {}

        with Live(table):
            with self._increase_timeout_to(30000):
                for line in self._client.push(
                    repository=self.repo, tag=self._tag, stream=True, decode=True
                ):
                    if "errorDetail" in line:
                        raise GreapDockerError(line["errorDetail"]["message"])
                    elif "id" not in line:
                        continue
                    status.update(line["status"])
                    if line["id"] not in tasks and line["progressDetail"]:
                        tasks[line["id"]] = progress.add_task(
                            f"[yellow]{line['status']}",
                            total=line["progressDetail"].get("total", 0),
                        )
                    elif line["id"] in tasks and line["progressDetail"]:
                        progress.update(
                            tasks[line["id"]],
                            completed=line["progressDetail"]["current"],
                        )
        return self
