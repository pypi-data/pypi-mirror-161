import json
import logging
import os
import pathlib
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import List, Optional, Union

import requests
from packaging.version import Version, parse

from databutton.version import __version__

logger = logging.getLogger("databutton.utils")


DEFAULT_GLOB_EXCLUDE = ["venv", ".venv", "__pycache__", ".databutton"]


@dataclass
class ProjectConfig:
    uid: str
    name: str
    # List of fnmatch patterns to exclude, similar to .gitignore
    exclude: Optional[List[str]] = field(default_factory=lambda: DEFAULT_GLOB_EXCLUDE)


CONFIG_FILENAME = "databutton.json"


def get_databutton_config_path() -> Path:
    project_directory = pathlib.Path.cwd()
    retries = 1  # Increase to re-enable feature looking in parent directories or clean up code
    for _ in range(retries):
        filepath = project_directory / CONFIG_FILENAME
        if filepath.exists():
            return filepath
        project_directory = project_directory.parent
        if not project_directory.is_relative_to(pathlib.Path.home()):
            break
    raise FileNotFoundError(
        "Could not find databutton.json config file in parent directories."
    )


def get_project_directory() -> Path:
    return get_databutton_config_path().parent


def get_databutton_config() -> ProjectConfig:
    with open(get_databutton_config_path(), "r") as f:
        config = json.load(f)
        return ProjectConfig(
            name=config["name"],
            uid=config["uid"],
            exclude=config["exclude"],
        )


def create_databutton_config(
    name: str, uid: str, project_directory: Path = None
) -> ProjectConfig:
    if project_directory is None:
        project_directory = pathlib.Path.cwd()
    config = ProjectConfig(
        name=name,
        uid=uid,
        exclude=DEFAULT_GLOB_EXCLUDE,
    )
    with open(project_directory / CONFIG_FILENAME, "w") as f:
        f.write(json.dumps(config.__dict__, indent=2))
        return config


def get_api_url(uid: str) -> str:
    u = os.environ.get("DATABUTTON_API_URL")
    return u or f"https://p{uid}.dbtn.app/dbtn"


@dataclass
class LoginData:
    refreshToken: str
    uid: str


def get_databutton_login_info() -> Optional[LoginData]:
    if "DATABUTTON_TOKEN" in os.environ:
        config = get_databutton_config()
        return LoginData(refreshToken=os.environ["DATABUTTON_TOKEN"], uid="token")

    auth_path = get_databutton_login_path()
    auth_path.mkdir(exist_ok=True, parents=True)

    uids = [f for f in os.listdir(auth_path) if f.endswith(".json")]
    if len(uids) > 0:
        # Just take a random one for now
        with open(auth_path / uids[0]) as f:
            config = json.load(f)
            return LoginData(uid=config["uid"], refreshToken=config["refreshToken"])
    return None


def get_databutton_login_path():
    return Path(Path.home(), ".config", "databutton")


def get_databutton_components_path():
    return Path(".databutton", "artifacts.json")


FIREBASE_CONFIG = {
    "apiKey": "AIzaSyAdgR9BGfQrV2fzndXZLZYgiRtpydlq8ug",
    "authDomain": "databutton.firebaseapp.com",
    "projectId": "databutton",
    "storageBucket": "databutton.appspot.com",
    "databaseURL": "",
}
storage_bucket = (
    f"https://firebasestorage.googleapis.com/v0/b/{FIREBASE_CONFIG['storageBucket']}"
)


def upload_to_bucket(
    file_buf, config: ProjectConfig, key: str, content_type: str = "text/csv"
):
    url = get_signed_dataframe_url(project_id=config.uid, key=key, method="PUT")

    response = requests.put(url, data=file_buf, headers={"content-type": content_type})
    if not response.ok:
        raise Exception(f"Could not upload to path {key}")
    return response


def get_signed_dataframe_url(project_id: Optional[str], key: str, method: str) -> str:
    """
    Gets a signed url to either get or put a dataframes
    args:
        key: The dataframe key
        method: GET or PUT
    """
    project_id = project_id or get_databutton_config().uid
    res = requests.get(
        "https://europe-west1-databutton.cloudfunctions.net/dataframes_signer",
        params={"data_key": key, "method": method, "project_id": project_id},
        headers={
            "Authorization": f"Bearer {get_auth_token()}",
            "x-databutton-release": os.environ.get("DATABUTTON_RELEASE"),
        },
    )
    if not res.ok:
        logger.debug(f"Failed getting dataframe {res.text}")
        raise Exception(f"Failed fetching dataframe with status_code {res.status_code}")
    try:
        return res.json()["signed_url"]
    except Exception as e:
        logger.debug("Failed getting dataframe")
        raise e


def download_from_bucket(key: str, config: ProjectConfig):
    url = get_signed_dataframe_url(config.uid, key, method="GET")

    response = requests.get(url)
    if not response.ok:
        if response.status_code == 404:
            raise FileNotFoundError(f"Could not find {key}")
        raise Exception(f"Could not download {key}")
    return response


_cached_auth_token = None


def get_auth_token() -> str:
    global _cached_auth_token
    # This has a 15 minute cache
    if _cached_auth_token is not None and time() - _cached_auth_token[0] > 60 * 15:
        _cached_auth_token = None
    if _cached_auth_token is None:
        login_info = get_databutton_login_info()
        if login_info is None:
            raise Exception(
                "Could not find any login information."
                "\nAre you sure you are logged in?"
            )
        res = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_CONFIG['apiKey']}",
            {"grant_type": "refresh_token", "refresh_token": login_info.refreshToken},
        )
        if not res.ok:
            raise Exception("Could not authenticate")
        json = res.json()
        _cached_auth_token = (time(), json["id_token"])
    return _cached_auth_token[1]


def create_databutton_cloud_project(name: str):
    """Creates a Databutton Cloud Project"""
    token = get_auth_token()

    res = requests.post(
        "https://europe-west1-databutton.cloudfunctions.net/createOrUpdateProject",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )

    res_json = res.json()
    new_id = res_json["id"]
    return new_id


def get_build_logs(build_id: str) -> str:
    log_url_response = requests.get(
        "https://europe-west1-databutton.cloudfunctions.net/get_cloud_build_logs",
        params={"build_id": build_id},
        headers={"Authorization": f"Bearer {get_auth_token()}"},
    )
    log_url = log_url_response.json()["signed_url"]
    return log_url


def get_newest_pip_databutton_version() -> Version:
    res = requests.get("https://pypi.python.org/pypi/databutton/json").json()
    v = parse("0")
    for version in res.get("releases").keys():
        vv = parse(version)
        if not vv.is_prerelease:
            v = max(v, vv)
    return v


def new_databutton_version_exists() -> Union[Version, bool]:
    try:
        current = parse(__version__)
        newest = get_newest_pip_databutton_version()
        if newest > current:
            return newest
        return False
    except Exception as e:
        logger.debug("Could not fetch new version", e)


def current_databutton_release():
    return os.environ.get("DATABUTTON_RELEASE", "")


def is_running_locally():
    return current_databutton_release() == ""
