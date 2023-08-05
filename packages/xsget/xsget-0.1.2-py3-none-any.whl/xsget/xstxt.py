# pylint: disable=unnecessary-lambda, duplicate-code
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

"""xstxt is a cli app that extract content from HTML to text file.

https://github.com/kianmeng/xsget
"""

import argparse
import asyncio
import glob
import logging
import sys

import aiofiles
import regex as re
from bs4 import BeautifulSoup, UnicodeDammit
from natsort import natsorted

from xsget import __version__, load_or_create_config, setup_logging
from xsget.book import Book
from xsget.chapter import Chapter

__usages__ = """
examples:
  xstxt -i *.html

"""

_logger = logging.getLogger(__name__)


def get_html_files(inputs, limit, excludes):
    """Get the list of HTML files or file for cleansing and extracting.

    Args:
        inputs (List[str]): Glob-like pattern for selecting HTML files
        limit (int): Number of HTML files to process
        excludes (List[str]): Glob-like pattern for excluding HTML files

    Returns:
        list: Number of HTML file names
    """
    input_files = []
    for pattern in inputs:
        _logger.debug("HTML source input: %s", pattern)
        found_files = glob.glob(pattern, recursive=True)
        if len(found_files) == 0:
            _logger.error("No input files found in: %s", pattern)

        input_files = input_files + found_files

    exclude_files = []
    for pattern in excludes:
        _logger.debug("HTML source exclude: %s", pattern)
        found_files = glob.glob(pattern, recursive=True)
        if len(found_files) == 0:
            _logger.error("No exclude files found in: %s", pattern)

        exclude_files = exclude_files + found_files

    files = natsorted(
        list(set(input_files) - set(exclude_files)), key=lambda p: str(p)
    )
    return files[:limit] if limit > 0 else files


async def gen_book(config):
    """Extract all chapters from HTML files into single text file.

    Args:
        config (map): Config for xstxt
    """
    html_files = get_html_files(config.input, config.limit, config.exclude)

    futures = []
    for filename in html_files:
        async with aiofiles.open(filename, "rb") as file:
            dammit = UnicodeDammit(await file.read())
            decoded_html = dammit.unicode_markup
            futures.append(
                extract_chapter(
                    decoded_html,
                    config.title_css_path,
                    config.body_css_path,
                    config.html_replace,
                    filename,
                )
            )

    chapters = await asyncio.gather(*futures)
    gen_txt(Book(chapters), config)


async def extract_chapter(
    decoded_html, title_css_path, body_css_path, html_replace=(), filename=""
):
    """Extract chapter from the decoded HTML.

    Args:
        decoded_html (str): decoded HTML text
        title_css_path (int): CSS path to a title of a page
        body_css_path (int): CSS path to a body of a page
        html_replace (list): list of search and replace item
        filename (str): the filename of the decoded html

    Returns:
        list(Chapter): list of extracted chapters
    """
    html = decoded_html
    if html_replace:
        html = search_and_replace(decoded_html, html_replace)

    soup = BeautifulSoup(html, features="lxml")
    title = extract_title(soup, title_css_path)
    body = extract_body(soup, body_css_path)

    chapter = Chapter(title, body.rstrip(), filename)
    _logger.info("Process %s", repr(chapter))
    return chapter


def extract_title(html, css_path):
    """Extract title of a chapter from HTML.

    Args:
        html (str): HTML text
        css_path (int): CSS path to a title of a chapter

    Returns:
        str: title of a chapter
    """
    if not css_path:
        return ""

    title = html.select_one(css_path)
    return title.text if title else ""


def extract_body(html, css_path):
    """Extract body of a chapter from HTML.

    Args:
        html (str): HTML text
        css_path (int): CSS path to a body of a chapter

    Returns:
        str: body of a chapter
    """
    if not css_path:
        return ""

    body = html.select_one(css_path)
    return body.text if body else ""


def search_and_replace(content, regexs):
    """Replace words/phrases based on a list of regex.

    Args:
        content (str): HTML or plain text
        regexs (list): List of regex rules

    Returns:
        str: HTML or plain text
    """
    try:
        for search, replace in regexs:
            _logger.debug("search: %s -> replace: %s", search, replace)
            before = re.compile(
                rf"{search}", re.MULTILINE  # pylint: disable=no-member
            )
            after = rf"{replace}"
            content = re.sub(before, after, content)
    except ValueError as error:
        _logger.error(error)

    return content


def gen_txt(book, config):
    """Write the extracted book into txt file.

    Args:
        book (list): A list of Chapters
        config (dict): Config file
    """
    with open(config.output, "w", newline="\n", encoding="utf8") as file:
        file.write(f"书名：{config.book_title}\n")
        file.write(f"作者：{config.book_author}\n\n")

        chapters = [str(chapter) for chapter in book.chapters]
        content = "\n\n".join(chapters)

        if config.txt_replace:
            content = search_and_replace(content, config.txt_replace)

        file.write(content)


def build_parser():
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(
        add_help=False,
        description=__doc__,
        epilog=__usages__,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-pt",
        default="title",
        dest="title_css_path",
        help="set css path of chapter title (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )
    parser.add_argument(
        "-pb",
        default="body",
        dest="body_css_path",
        help="set css path of chapter body (default: '%(default)s')",
        type=str,
        metavar="CSS_PATH",
    )
    parser.add_argument(
        "-rh",
        default=[],
        action="append",
        dest="html_replace",
        nargs=2,
        help="set regex to replace word or pharase in html file",
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "-rt",
        default=[],
        action="append",
        dest="txt_replace",
        nargs=2,
        help="set regex to replace word or pharase in txt file",
        type=str,
        metavar="REGEX",
    )
    parser.add_argument(
        "-bt",
        default="不详",
        dest="book_title",
        help="set title of the novel (default: '%(default)s')",
        type=str,
        metavar="TITLE",
    )
    parser.add_argument(
        "-ba",
        default="不详",
        dest="book_author",
        help="set author of the novel (default: '%(default)s')",
        type=str,
        metavar="AUTHOR",
    )
    parser.add_argument(
        "-i",
        default=["./*.html"],
        action="append",
        dest="input",
        help=(
            "set glob pattern of html files to process "
            "(default: '%(default)s')"
        ),
        type=str,
        metavar="GLOB_PATTERN",
    )
    parser.add_argument(
        "-e",
        default=[],
        action="append",
        dest="exclude",
        help=(
            "set glob pattern of html files to exclude "
            "(default: '%(default)s')"
        ),
        type=str,
        metavar="GLOB_PATTERN",
    )
    parser.add_argument(
        "-l",
        default=3,
        dest="limit",
        help="set number of html files to process (default: '%(default)s')",
        type=int,
        metavar="TOTAL_FILES",
    )
    parser.add_argument(
        "-o",
        default="book.txt",
        dest="output",
        help="set output txt file name (default: '%(default)s')",
        type=str,
        metavar="FILENAME",
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-g",
        nargs="?",
        default=False,
        const="xstxt.toml",
        dest="gen_config",
        help="generate config file from options (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
    )

    group.add_argument(
        "-c",
        nargs="?",
        default=False,
        const="xstxt.toml",
        dest="config",
        help="load config from file (default: '%(const)s')",
        type=str,
        metavar="FILENAME",
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


def run(config):
    """Run the asyncio main flow."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(gen_book(config))
    loop.close()


def main(args=None):
    """Run the main program flow."""
    parsed_args = argparse.Namespace(debug=True)
    try:
        parser = build_parser()
        parsed_args = parser.parse_args(args)

        setup_logging(parsed_args.debug)

        config = load_or_create_config(parsed_args, "xstxt")
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
