# Copyright (C) 2021,2022 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Console tools to download online novel and convert to text file."""

import logging
import sys
from argparse import Namespace
from importlib.resources import read_text
from pathlib import Path
from typing import Dict, List, Union

import tomlkit

__version__ = "0.1.2"

_logger = logging.getLogger(__name__)


class ConfigFileCorruptedError(Exception):
    """Config file corrupted after reading."""


class ConfigFileExistsError(Exception):
    """Config file found when generating a new config file."""


def setup_logging(debug: bool = False) -> None:
    """Set up logging by level."""
    conf = {
        True: {
            "level": logging.DEBUG,
            "msg": "[%(asctime)s] %(levelname)s: %(name)s: %(message)s",
        },
        False: {"level": logging.INFO, "msg": "%(message)s"},
    }

    logging.basicConfig(
        level=conf[debug]["level"],
        stream=sys.stdout,
        format=conf[debug]["msg"],
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def load_or_create_config(
    parsed_args: Namespace, app: str
) -> Dict[str, Union[str, List[str], int, bool]]:
    """Load config from file or create config to file."""
    config = vars(parsed_args)

    if parsed_args.config:
        config = _load_config(parsed_args)
    elif parsed_args.gen_config:
        config = _create_config(parsed_args, app)

    return config


def _load_config(parsed_args):
    """Load the config from command line options or from config file."""
    config_file = parsed_args.config
    with open(config_file, "r", encoding="utf8") as file:
        toml = tomlkit.load(file)

        if len(toml) == 0:
            raise ConfigFileCorruptedError(
                f"Corrupted config file: {config_file}"
            )

        _logger.info("Load from config file: %s", config_file)
        _logger.debug(toml)

        return toml


def _create_config(parsed_args, app):
    """Create config to toml file."""
    config_filename = parsed_args.gen_config

    if Path(config_filename).exists():
        raise ConfigFileExistsError(
            f"Existing config file found: {config_filename}"
        )

    with open(config_filename, "w", encoding="utf8") as file:
        config_dict = vars(parsed_args)
        _logger.debug(config_dict)

        toml = read_text(__package__, f"{app}.toml")
        doc = tomlkit.parse(toml)

        for key, value in config_dict.items():
            if key in doc:
                doc[key] = value

        file.write(tomlkit.dumps(doc))
        _logger.info("Create config file: %s", config_filename)

        return vars(parsed_args)
