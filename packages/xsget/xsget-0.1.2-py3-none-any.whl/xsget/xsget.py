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

"""xsget is a console app that crawl and download online novel.

https://github.com/kianmeng/xsget
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup, UnicodeDammit
from user_agent import generate_user_agent

from xsget import __version__, load_or_create_config, setup_logging

CONFIG_FILE = "xsget.toml"

__usages__ = """
examples:
  xsget http://localhost

"""

_logger = logging.getLogger(__name__)


def url_to_filename(url, url_param_as_filename=False):
    """Convert an URL to a filename.

    Args:
        url (str): An URL to be converted.
        url_param_as_filename (str|bool): Extract the set URL param value as
        filename. Default to False.

    Returns:
        str: The generated filename.
    """
    parsed_url = urlparse(unquote(url))

    if url_param_as_filename:
        query = parse_qs(parsed_url.query)
        if url_param_as_filename in query:
            return "".join(query[url_param_as_filename]) + ".html"

    return (
        parsed_url.path.rstrip("/").split("/")[-1].replace(".html", "")
        + ".html"
    )


def is_relative_url(url):
    """Check if an URL is a relative URL or URL without schema.

    Args:
        url(str): An URL for verification.

    Returns:
        bool: Whether the URL is relative or without schema.
    """
    uparse = urlparse(url)
    return uparse.netloc == "" or uparse.scheme == ""


def relative_to_absolute_url(base_url, path):
    """Convert relative URL to absolute URL.

    Args:
        base_url(str): The base URL.
        path(str): The path of an URL.

    Returns:
        str: The full absolute URL.
    """
    return urljoin(base_url, path)


def extract_urls(decoded_html, config):
    """Extract URLs from HTML base on the CSS Path.

    Args:
        decoded_html (str): The decoded HTML string
        config (argparse.Namespace): Config from command line

    Returns:
        list: A list of URL for downloading
    """
    html = BeautifulSoup(decoded_html, features="lxml")
    urls = []

    for atag in html.select(config.link_css_path):
        page_url = atag.get("href")
        if page_url and is_relative_url(page_url):
            page_url = relative_to_absolute_url(config.url, page_url)

        urls.append(page_url)

    return urls


async def fetch_url(session, url, url_param_as_filename):
    """Fetch and save a single URL asynchronously.

    Args:
        session (str): Async session client
        url (str): The URL to download
        url_param_as_file (boolean): Treat the URL param as file?

    Returns:
        None
    """
    async with session.get(url) as resp:
        try:
            resp.raise_for_status()

            content = await resp.text(encoding="gb18030")
            filename = url_to_filename(str(resp.url), url_param_as_filename)

            with open(filename, "w", encoding="gb18030") as file:
                file.write(content)
                _logger.info(
                    "Fetch: %s -> save: %s", unquote(str(resp.url)), filename
                )

        except aiohttp.ClientResponseError as error:
            _logger.error(error)


async def fetch_urls(urls, url_param_as_filename):
    """Batch fetch and save multiple URLS asynchronously.

    Args:
        urls (list): A list of URL to be fetched
        url_param_as_file (boolean): Treat the URL param as file?

    Returns:
        None
    """
    async with aiohttp.ClientSession(headers=http_headers()) as session:
        futures = []
        for url in urls:
            filename = url_to_filename(url, url_param_as_filename)
            if Path(filename).exists():
                _logger.info("Found file: %s, skip download", filename)
            else:
                futures.append(fetch_url(session, url, url_param_as_filename))

        await asyncio.gather(*futures)


def http_headers():
    """Set the user agent for the crawler.

    Returns:
        tuple: Custom HTTP headers, but only User-Agent for now
    """
    return {"User-Agent": generate_user_agent()}


def build_parser(args=None):
    """Build the CLI parser."""
    args = args or []

    parser = argparse.ArgumentParser(
        add_help=False,
        description=__doc__,
        epilog=__usages__,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        dest="url",
        nargs="?" if "-c" in args or not sys.stdin.isatty() else None,
        help="set url of the index page to crawl",
        type=str,
        default=sys.stdin.read() if not sys.stdin.isatty() else None,
        metavar="URL",
    )

    parser.add_argument(
        "-l",
        default="a",
        dest="link_css_path",
        help="set css path of the link to a chapter (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )

    parser.add_argument(
        "-p",
        default="",
        dest="url_param_as_filename",
        help="use url param key as filename (default: '')",
        type=str,
        metavar="URL_PARAM",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-g",
        nargs="?",
        default=False,
        const=CONFIG_FILE,
        dest="gen_config",
        help="generate config file from options (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    group.add_argument(
        "-c",
        nargs="?",
        default=False,
        const=CONFIG_FILE,
        dest="config",
        help="load config from file (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    parser.add_argument(
        "-r",
        action="store_true",
        dest="refresh",
        help="refresh the index page",
    )

    parser.add_argument(
        "-t",
        action="store_true",
        dest="test",
        help="show extracted urls without crawling",
    )

    parser.add_argument(
        "-d",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stacktrace",
    )

    parser.add_argument(
        "-h",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )

    parser.add_argument(
        "-v", action="version", version=f"%(prog)s {__version__}"
    )

    return parser


def run(config: argparse.Namespace) -> None:
    """Run the asyncio main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments or
        config file.
    """
    filename = url_to_filename(config.url, config.url_param_as_filename)

    if config.refresh:
        _logger.info("Refresh the index url: %s", config.url)
        index_html = Path(filename)
        if index_html.exists():
            index_html.unlink()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        fetch_urls([config.url], config.url_param_as_filename)
    )

    with open(filename, "rb") as file:
        dammit = UnicodeDammit(file.read())
        decoded_html = dammit.unicode_markup
        eurls = extract_urls(decoded_html, config)

        if config.test:
            for eurl in eurls:
                _logger.info("Found url: %s", eurl)
        else:
            loop.run_until_complete(
                fetch_urls(eurls, config.url_param_as_filename)
            )

        loop.close()


def main(args):
    """Run the main program flow."""
    parsed_args = argparse.Namespace(debug=True)
    try:
        parser = build_parser(args)
        parsed_args = parser.parse_args(args)

        setup_logging(parsed_args.debug)

        config = load_or_create_config(parsed_args, "xsget")
        parser.set_defaults(**config)
        config = parser.parse_args()

        run(config)
    except Exception as error:
        msg = error.message if hasattr(error, "message") else str(error)
        _logger.error(msg, exc_info=parsed_args.debug)
        raise SystemExit(1) from None


def cli():
    """Set the main entrypoint of the console app."""
    main(sys.argv[1:])


if __name__ == "__main__":
    cli()  # pragma: no cover
    raise SystemExit()  # pragma: no cover
