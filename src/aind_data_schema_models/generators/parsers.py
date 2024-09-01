import csv
import os
from typing import Dict, List, Optional

import requests
import yaml


def csv_parser(value: os.PathLike, fieldnames: Optional[List[str]] = None) -> List[Dict[str, str]]:
    with open(value, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f, fieldnames=fieldnames))


def get_who_am_i_list(
    url: str = "https://raw.githubusercontent.com/harp-tech/protocol/main/whoami.yml",
) -> List[Dict[str, str]]:
    response = requests.get(url, allow_redirects=True, timeout=5)
    content = response.content.decode("utf-8")
    content = yaml.safe_load(content)
    devices = content["devices"]
    return [{"name": device["name"], "whoami": str(whoami)} for whoami, device in devices.items()]
