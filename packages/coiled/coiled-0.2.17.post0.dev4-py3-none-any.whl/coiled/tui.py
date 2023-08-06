import asyncio
import datetime
from typing import Dict

from coiled._beta import CloudBeta
from coiled.core import Async
from dask.utils import format_bytes, format_time
from rich.align import Align
from rich.console import RenderableType
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from textual import events
from textual.app import App, Reactive, Widget
from textual.widgets import ScrollView

STATUS_ICON = {
    "running": "🟢",
    "stopped": "🔴",
}


class ClusterTable(Widget):
    selected_index: Reactive[int] = Reactive(0)
    has_focus: Reactive[bool] = Reactive(False)
    data: Reactive[Dict[str, Dict]] = Reactive({})

    def render(self):
        table = Table(
            expand=True,
            box=None,
            show_edge=True,
        )
        table.add_column("", no_wrap=True)
        table.add_column("id", no_wrap=True)
        table.add_column("created", no_wrap=True)
        table.add_column("workers", no_wrap=True)
        table.add_column("memory", no_wrap=True)
        table.add_column("n_tasks", no_wrap=True)
        table.add_column("time")
        table.add_column("$")
        for i, (name, dask_scheduler) in enumerate(self.data.items()):
            running = dask_scheduler["status"] == "running"
            table.add_row(
                STATUS_ICON[dask_scheduler["status"]],
                name.split("-")[1],
                dask_scheduler["created"].split("T")[0],
                str(dask_scheduler["workers"]) if running else "",
                format_bytes(dask_scheduler["memory"])
                + " / "
                + format_bytes(dask_scheduler["memory_limit"])
                if running
                else "",
                str(dask_scheduler["n_tasks"]),
                format_time(dask_scheduler["thread_seconds"]),
                "$%.2f" % (0.06 * dask_scheduler["thread_seconds"] / 3600),
                style="reverse" if self.selected_index == i else None,
            )

        return table


class Computations(Widget):
    data: Reactive[list] = Reactive([])

    def render(self):
        table = Table(
            expand=True,
            box=None,
            show_edge=True,
        )
        table.add_column("Code")
        table.add_column("Duration")
        for computation in self.data:
            start = datetime.datetime.fromisoformat(computation["start"])
            stop = datetime.datetime.fromisoformat(computation["stop"])
            table.add_row(
                Markdown("```python\n" + computation["code"] + "\n```"),
                format_time((stop - start).total_seconds()),
            )

        return table


class CoiledHeader(Widget):
    def render(self) -> RenderableType:
        return Panel(
            Align.center("Coiled", vertical="middle"),
            highlight=True,
            border_style="blue",
        )


class MyRule(Widget):
    def __init__(self, text):
        self.text = text
        Widget.__init__(self, name=text)

    def render(self):
        return Rule(self.text)


class CoiledUI(App):
    async def on_load(self) -> None:
        """Sent before going in to application mode."""
        await self.bind("q", "quit", "Quit")
        # TODO: Figure out why pyright is failing in this next line
        self.c: CloudBeta[Async] = await CloudBeta(asynchronous=True)  # type: ignore
        self.cluster_list = ClusterTable(name="Clusters")
        self.cluster_view = ScrollView(self.cluster_list, fluid=True)
        self.computations_list = Computations(name="Computations")
        self.computations_view = ScrollView(self.computations_list, fluid=True)

        await self._update_clusters()
        asyncio.create_task(self.update_clusters())
        asyncio.create_task(self.update_cluster())

    async def update_clusters(self) -> None:
        while True:
            await self._update_clusters()
            await asyncio.sleep(1)

    async def update_cluster(self) -> None:
        while True:
            await self._update_cluster()
            await asyncio.sleep(1)

    async def _update_clusters(self) -> None:
        clusters, _ = await self.c._list_dask_scheduler_page(0)
        clusters = {c["scheduler_id"]: c for c in clusters}
        self.cluster_list.data = clusters
        await self.cluster_view.update(self.cluster_list, home=False)

    async def _update_cluster(self):
        i = self.cluster_list.selected_index
        cluster = list(self.cluster_list.data.values())[i]
        # TODO: Figure out why pyright is failing in this next line
        self.computations_list.data = await self.c._list_computations(cluster["id"])  # type: ignore

    async def close_cluster(self):
        i = self.cluster_list.selected_index
        cluster = list(self.cluster_list.data.values())[i]
        await self.c._send_state(cluster["id"], desired_status="stopped")

    async def on_mount(self) -> None:
        await self.view.dock(CoiledHeader(), edge="top", name="header", size=3)
        await self.view.dock(
            self.cluster_view,
            size=10,
            edge="top",
            name="cluster_list",
        )
        await self.view.dock(
            MyRule("Computations"), edge="top", name="computations", size=3
        )

        await self.view.dock(
            self.computations_view,
            edge="top",
            name="computations",
        )

    async def on_key(self, event: events.Key) -> None:
        i = self.cluster_list.selected_index
        if event.key == "up":
            self.cluster_list.selected_index = (i - 1) % len(self.cluster_list.data)
        elif event.key == "down":
            self.cluster_list.selected_index = (i + 1) % len(self.cluster_list.data)
        elif event.key == "enter":
            await self._update_cluster()
        elif event.key == "delete":
            await self.close_cluster()


def show():
    app = CoiledUI()
    app.run(log="coiled.log")


if __name__ == "__main__":
    show()
