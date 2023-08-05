import asyncio
import json
import logging
import platform
import re
import typing
from asyncio import Lock
from collections import defaultdict
from hashlib import md5
from logging import getLogger
from os import environ
from pathlib import Path
from typing import Iterable, Optional

import aiohttp
import pkg_resources
from dask import config
from importlib_metadata import distributions
from packaging import specifiers, version
from packaging.utils import parse_wheel_filename
from typing_extensions import TypedDict

logger = getLogger("coiled.auto_env")
subdir_datas = {}
cache_dir = Path(config.PATH) / "coiled-cache"
PYTHON_VERSION = platform.python_version_tuple()


class PackageInfo(TypedDict):
    name: str
    client_version: str
    specifier: str
    include: bool


class CondaPackageInfo(PackageInfo):
    channel: str


class PipPackageInfo(PackageInfo):
    pass


class CondaPackage:
    def __init__(self, meta_json: typing.Dict):
        self.name = meta_json["name"]
        self.version = meta_json["version"]
        self.subdir = meta_json["subdir"]
        channel_regex = f"(.*)/(.*)/{self.subdir}"
        result = re.match(channel_regex, meta_json["channel"])
        assert result
        self.channel_url = result.group(1) + "/" + result.group(2)
        self.channel = result.group(2)


def create_specifier(v: str) -> specifiers.SpecifierSet:
    try:
        parsed_version = version.parse(v)
        if isinstance(parsed_version, version.LegacyVersion):
            return specifiers.SpecifierSet(f"=={v}")
        else:
            if len(v.split(".")) == 1:
                # ~= cannot be used with single section versions
                # https://peps.python.org/pep-0440/#compatible-release
                return specifiers.SpecifierSet(
                    f"=={v}",
                    prereleases=parsed_version.is_prerelease,
                )
            elif parsed_version.is_prerelease:
                return specifiers.SpecifierSet(
                    f"~={v}",
                    prereleases=True,
                )
            else:
                return specifiers.SpecifierSet(
                    f"~={v}",
                )
    except version.InvalidVersion:
        return specifiers.SpecifierSet(f"=={v}")


def any_matches(versions: Iterable[str], specifier: specifiers.SpecifierSet):
    for available_version in versions:
        if specifier and available_version in specifier:
            return True
    else:
        return False


class RepoCache:
    # This is not thread safe if there are multiple loops
    channel_memory_cache: typing.DefaultDict[
        str, typing.DefaultDict[str, typing.Dict]
    ] = defaultdict(lambda: defaultdict(dict))

    def __init__(self):
        self.lock = Lock()

    async def fetch(self, channel: str) -> typing.Dict[str, typing.Dict]:
        channel_filename = Path(md5(channel.encode("utf-8")).hexdigest()).with_suffix(
            ".json"
        )
        async with self.lock:
            # check again once we have the lock in case
            # someone beat us to it
            if not self.channel_memory_cache.get(channel):
                if not cache_dir.exists():
                    cache_dir.mkdir(parents=True)
                channel_fp = cache_dir / channel_filename
                headers = {}
                channel_cache_meta_fp = channel_fp.with_suffix(".meta_cache")
                if channel_fp.exists():
                    with channel_cache_meta_fp.open("r") as cache_meta_f:
                        channel_cache_meta = json.load(cache_meta_f)
                    headers["If-None-Match"] = channel_cache_meta["etag"]
                    headers["If-Modified-Since"] = channel_cache_meta["mod"]
                async with aiohttp.ClientSession() as client:
                    resp = await client.get(
                        channel + "/" + "repodata.json", headers=headers
                    )
                    if resp.status == 304:
                        logger.info(f"Loading cached conda repodata for {channel}")
                        data = json.loads(channel_fp.read_text())
                    else:
                        logger.info(f"Downloading fresh conda repodata for {channel}")
                        data = await resp.json()
                        channel_fp.write_text(json.dumps(data))
                        channel_cache_meta_fp.write_text(
                            json.dumps(
                                {
                                    "etag": resp.headers["Etag"],
                                    "mod": resp.headers["Last-Modified"],
                                }
                            )
                        )
                    for pkg in data["packages"].values():
                        self.channel_memory_cache[channel][pkg["name"]][
                            pkg["version"]
                        ] = pkg
                return self.channel_memory_cache[channel]
            else:
                return self.channel_memory_cache[channel]


async def handle_conda_package(pkg_fp: Path, cache: RepoCache):
    pkg = CondaPackage(json.load(pkg_fp.open("r")))
    specifier = create_specifier(pkg.version)

    package_info: CondaPackageInfo = {
        "channel": pkg.channel,
        "name": pkg.name,
        "client_version": pkg.version,
        "specifier": str(specifier),
        "include": True,
    }
    if pkg.subdir != "noarch":
        repo_data = await cache.fetch(channel=pkg.channel_url + "/linux-64")
        if repo_data.get(pkg.name):
            if not any_matches(
                versions=repo_data[pkg.name].keys(), specifier=specifier
            ):
                package_info["include"] = False
        else:
            package_info["include"] = False
    return package_info


async def iterate_conda_packages(prefix: Path):
    conda_meta = prefix / "conda-meta"
    cache = RepoCache()

    if conda_meta.exists() and conda_meta.is_dir():
        packages = await asyncio.gather(
            *[
                handle_conda_package(metafile, cache)
                for metafile in conda_meta.iterdir()
                if metafile.suffix == ".json"
            ]
        )
        return {pkg["name"]: pkg for pkg in packages}
    else:
        return {}


async def create_conda_env_approximation():
    conda_default_env = environ.get("CONDA_DEFAULT_ENV")
    conda_prefix = environ.get("CONDA_PREFIX")
    if conda_default_env and conda_prefix:
        logger.info(f"Conda environment detected: {conda_default_env}")
        conda_env: typing.Dict[str, CondaPackageInfo] = {}
        return await iterate_conda_packages(prefix=Path(conda_prefix))
    else:
        # User is not using conda, we should just grab their python version
        # so we know what to install
        conda_env: typing.Dict[str, CondaPackageInfo] = {
            "python": {
                "name": "python",
                "client_version": platform.python_version(),
                "specifier": f"=={platform.python_version()}",
                "include": True,
                "channel": "conda-forge",
            }
        }
    return conda_env


from packaging.tags import Tag


class PipRepo:
    def __init__(self, client: aiohttp.ClientSession):
        self.client = client
        self.looking_for = [
            Tag(f"py{PYTHON_VERSION[0]}", "none", "any"),
            Tag(f"cp{PYTHON_VERSION[0]}{PYTHON_VERSION[1]}", "none", "any"),
        ]

    async def fetch(self, package_name):
        resp = await self.client.get(f"https://pypi.org/pypi/{package_name}/json")
        data = await resp.json()
        pkgs = {}
        for build_version, builds in data["releases"].items():
            for build in [
                b
                for b in builds
                if not b.get("yanked")
                and b["packagetype"] not in ["bdist_dumb", "bdist_wininst", "bdist_rpm"]
            ]:
                if build["packagetype"] == "bdist_wheel":
                    _, _, _, tags = parse_wheel_filename(build["filename"])
                elif build["packagetype"] == "sdist":
                    tags = [
                        Tag(f"py{PYTHON_VERSION[0]}", "none", "any"),
                    ]
                else:
                    dist = pkg_resources.Distribution.from_filename(build["filename"])
                    tags = [Tag(f"py{dist.py_version}", "none", "any")]
                if any(valid in tags for valid in self.looking_for):
                    pkgs[build_version] = build
        return pkgs


async def handle_dist(dist, repo: PipRepo) -> Optional[PipPackageInfo]:
    installer = dist.read_text("INSTALLER")
    name = dist.metadata.get("Name")
    if not name:
        logger.warning(f"Omitting package missing name, located at {dist._path}")
        return None
    if installer:
        installer = installer.rstrip()
        if installer == "pip":
            specifier = create_specifier(dist.version)
            data = await repo.fetch(name)
            if not any_matches(versions=data.keys(), specifier=specifier):
                return {
                    "name": name,
                    "client_version": dist.version,
                    "specifier": str(specifier),
                    "include": False,
                }

            return {
                "name": name,
                "client_version": dist.version,
                "specifier": str(specifier),
                "include": True,
            }
        elif not installer == "conda":
            logger.warning(
                f"{name} was installed by the unrecognized installer {installer} and has been omitted"
            )
            return None


async def create_pip_env_approximation() -> typing.Dict[str, PipPackageInfo]:
    async with aiohttp.ClientSession() as client:
        pip_repo = PipRepo(client=client)
        return {
            pkg["name"]: pkg
            for pkg in await asyncio.gather(
                *(handle_dist(dist, repo=pip_repo) for dist in distributions())
            )
            if pkg
        }
    raise Exception("Should not get here")


async def create_environment_approximation() -> typing.Tuple[
    typing.List[PipPackageInfo], typing.List[CondaPackageInfo]
]:
    # TODO: path deps
    # TODO: private conda channels
    # TODO: remote git deps (public then private)
    # TODO: detect pre-releases and only set --pre flag for those packages (for conda)
    conda_env_future = asyncio.create_task(create_conda_env_approximation())
    pip_env_future = asyncio.create_task(create_pip_env_approximation())
    conda_env = await conda_env_future
    pip_env = await pip_env_future
    for required_dep in ["dask", "distributed", "bokeh"]:
        if required_dep not in conda_env and required_dep not in pip_env:
            raise ValueError(
                f"{required_dep} is not detected your environment. You must install these packages"
            )
    has_dropped = False
    for pkg in conda_env.values():
        if not pkg["include"]:
            has_dropped = True
            logger.info(
                f'Conda: package {pkg["name"]}-{pkg["client_version"]} '
                "not available for linux-x86-64bit environment. Will not be installed. "
            )
    for pkg in pip_env.values():
        if not pkg["include"]:
            has_dropped = True
            logger.info(
                f'Conda: package {pkg["name"]}-{pkg["client_version"]} not available'
                " for linux-x86-64bit environment. Will not be installed."
            )
    if has_dropped:
        logger.info(
            "If the dropped packages are dependencies you require,"
            " install a version that has a linux-x86-64bit build available"
        )

    return list(pip_env.values()), list(conda_env.values())


if __name__ == "__main__":
    from logging import basicConfig

    basicConfig(level=logging.INFO)
    import pprint

    pprint.pprint(asyncio.run(create_environment_approximation()))
