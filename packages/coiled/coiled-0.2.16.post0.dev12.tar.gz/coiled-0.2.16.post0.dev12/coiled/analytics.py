from __future__ import annotations

from types import ModuleType
from typing import Optional

import coiled
import dask
import urllib3
from dask.distributed import Client, get_client
from dask.utils import has_keyword


def register(client: Optional[Client] = None):
    """
    Register Coiled analytics with your Dask cluster.

    Parameters
    ----------
    client:
        The Dask client that you want to connect to
        This will use the most recently created Dask client by default
        (usually what you want anyway)

    Examples
    --------
    >>> from dask.distributed import Client
    >>> client = Client()

    >>> import coiled.analytics
    >>> coiled.analytics.register()

    Or use this module as a preload

    $ dask-scheduler --preload coiled.analytics
    """
    with coiled.Cloud():  # verify that we can log in
        pass
    client = client or get_client()

    url = dask.config.get("coiled.server") + "/api/v2/analytics/preload"
    with urllib3.PoolManager() as http:
        response = http.request("GET", url)

    if response.status != 200:
        raise Exception("Unable to collect Coiled plugin", response.status)

    compiled = compile(response.data, url, "exec")
    module = ModuleType(url)
    exec(compiled, module.__dict__)
    plugin = module.CoiledTelemetry()  # type: ignore

    if has_keyword(client.register_scheduler_plugin, "idempotent"):  # type: ignore
        client.register_scheduler_plugin(plugin, idempotent=True)  # type: ignore
    else:
        client.register_scheduler_plugin(plugin)  # type: ignore


def list_clusters(
    account: Optional[str] = None,
    since: Optional[str] = "7 days",
    user: Optional[str] = None,
):
    """List clusters associated to this account

    Clusters arrive in reverse chronological order (the first element is the
    most recent).

    Parameters
    ----------
    account:
        The account whose clusters you want to list
        You must be a member of this account
        Your default account will be used if none is provided
    since:
        The amount of time to go back in history to list clusters.
        Defaults to seven days.  Leave as ``None`` to collect all history.
        Accepts any value parseable by dask.utils.parse_timedelta
    user:
        Optionally filter on username
        Providing ``None`` selects all users

    Examples
    --------
    >>> import coiled.analytics
    >>> coiled.analytics.list_clusters()  # doctest: +SKIP
    >>> coiled.analytics.list_clusters(since="30 days", user="alice")  # doctest: +SKIP
    """
    with coiled.Cloud() as c:
        return c.list_dask_scheduler(account=account, since=since, user=user)


def list_computations(cluster_id: int, account: Optional[str] = None):
    """List computations associated to a cluster

    Parameters
    ----------
    cluster_id:
        The identifier of the cluster that you want to select
    account:
        The account whose clusters you want to list
        You must be a member of this account
        Your default account will be used if none is provided

    Examples
    --------
    >>> import coiled.analytics
    >>> clusters = coiled.analytics.list_clusters()  # doctest: +SKIP
    >>> coiled.analytics.list_computations(clusters[0]["id"])  # doctest: +SKIP

    See Also
    --------
    list_clusters
    """
    with coiled.Cloud() as c:
        return c.list_computations(cluster_id, account=account)


def list_events(cluster_id: int, account: Optional[str] = None):
    """List events associated to a cluster

    Parameters
    ----------
    cluster_id:
        The identifier of the cluster that you want to select
    account:
        The account whose clusters you want to list
        You must be a member of this account
        Your default account will be used if none is provided

    Examples
    --------
    >>> import coiled.analytics
    >>> clusters = coiled.analytics.list_clusters()  # doctest: +SKIP
    >>> coiled.analytics.list_events(clusters[0]["id"])  # doctest: +SKIP

    See Also
    --------
    list_clusters
    """
    with coiled.Cloud() as c:
        return c.list_events(cluster_id, account=account)


def close(cluster_id: int, account: Optional[str] = None):
    """Close a cluster

    This sends a request to the remote scheduler asking it to shut down.
    It calls Scheduler.close on that machine.
    It is common (although not guaranteed) that workers should shut themselves
    down after a suitable time.

    Parameters
    ----------
    cluster_id:
        The identifier of the cluster that you want to select
    account:
        The account whose clusters you want to list
        You must be a member of this account
        Your default account will be used if none is provided

    Examples
    --------
    >>> import coiled.analytics
    >>> clusters = coiled.analytics.list_clusters()  # doctest: +SKIP
    >>> coiled.analytics.close(clusters[0]["id"])  # doctest: +SKIP

    See Also
    --------
    list_clusters
    """
    with coiled.Cloud() as c:
        return c.send_state(cluster_id, account=account, desired_status="stopped")


def list_exceptions(
    account: Optional[str] = None,
    since: Optional[str] = "7 days",
    user: Optional[str] = None,
    cluster_id: Optional[int] = None,
):
    """List user exceptions

    Parameters
    ----------
    account (optional):
        The account whose clusters you want to list
        You must be a member of this account
        Your default account will be used if none is provided
    since (optional):
        The amount of time to go back in history to list clusters.
        Defaults to seven days.  Leave as ``None`` to collect all history.
        Accepts any value parseable by dask.utils.parse_timedelta
    user (optional):
        Optionally filter on username
        Providing ``None`` selects all users
    cluster_id (optional):
        The identifier of the cluster that you want to select

    Examples
    --------
    >>> import coiled.analytics
    >>> coiled.analytics.list_exceptions()  # doctest: +SKIP
    >>> coiled.analytics.list_exceptions(since="30 days", user="alice")  # doctest: +SKIP
    """
    with coiled.Cloud() as c:
        return c.list_exceptions(
            account=account, since=since, user=user, cluster_id=cluster_id
        )


async def dask_setup(scheduler):
    url = dask.config.get("coiled.server") + "/api/v2/analytics/preload"
    with urllib3.PoolManager() as http:
        response = http.request("GET", url)

    if response.status != 200:
        raise Exception("Unable to collect Coiled plugin", response.status)

    compiled = compile(response.data, url, "exec")
    module = ModuleType(url)
    exec(compiled, module.__dict__)
    plugin = module.CoiledTelemetry()  # type: ignore
    if plugin.name in scheduler.plugins:
        return

    scheduler.add_plugin(plugin, name=plugin.name, idempotent=True)
    await plugin.start(scheduler)


if __name__ == "__main__":
    from .tui import show

    show()
