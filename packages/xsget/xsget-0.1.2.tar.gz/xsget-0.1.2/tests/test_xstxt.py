# pylint: disable=missing-module-docstring,missing-function-docstring
import argparse
import re
from pathlib import Path

import pytest

from xsget import __version__
from xsget.book import Book
from xsget.chapter import Chapter
from xsget.xstxt import (
    extract_chapter,
    gen_txt,
    get_html_files,
    search_and_replace,
)


def test_version(script_runner):
    ret = script_runner.run("xstxt", "-v")
    assert f"xstxt {__version__}" in ret.stdout


def test_default_value_for_option_in_help(script_runner):
    ret = script_runner.run("xstxt", "-h")

    assert "set css path of chapter title (default: 'title')" in ret.stdout
    assert "set css path of chapter body (default: 'body')" in ret.stdout
    assert "set title of the novel (default: '不详')" in ret.stdout
    assert "set author of the novel (default: '不详')" in ret.stdout
    assert (
        "set glob pattern of html files to process (default: '['./*.html']')"
        in ret.stdout
    )
    assert (
        "set glob pattern of html files to exclude (default: '[]')"
        in ret.stdout
    )
    assert "set number of html files to process (default: '3')" in ret.stdout
    assert "set output txt file name (default: 'book.txt')" in ret.stdout
    assert (
        "generate config file from options (default: 'xstxt.toml')"
        in ret.stdout
    )
    assert "load config from file (default: 'xstxt.toml')" in ret.stdout


def test_get_html_files_sorted_in_natural_order(tmpdir):
    for name in ["200", "2", "100"]:
        tmpdir.join(f"{name}.html").write("")

    path = str(tmpdir)
    assert get_html_files([f"{path}/*.html"], 0, []) == [
        f"{path}/2.html",
        f"{path}/100.html",
        f"{path}/200.html",
    ]


def test_get_single_html_file(tmpdir):
    single = tmpdir.join("single.html")
    single.write("")

    path = str(tmpdir)
    assert get_html_files([f"{path}/single.html"], 0, []) == [
        f"{path}/single.html"
    ]


def test_get_html_files_by_limit(tmpdir):
    for i in range(0, 5):
        tmpdir.join(f"{i}.html").write("")

    path = str(tmpdir)
    assert get_html_files([f"{path}/*.html"], 3, []) == [
        f"{path}/0.html",
        f"{path}/1.html",
        f"{path}/2.html",
    ]


def test_get_no_html_files(caplog):
    path = "foobar/*.html"
    assert get_html_files([path], 0, []) == []
    assert f"No input files found in: {path}" in caplog.text


@pytest.mark.asyncio()
async def test_extract_chapter():
    html = """
        <html>
        <head><title>My Title</title></head>
        <body>
            <div id="content">My Content</div>
        </body>
        </html>
    """
    chapter = await extract_chapter(html, "title", "div#content")
    chapter.filename = "123.html"
    assert chapter.filename == "123.html"
    assert chapter.title == "My Title"
    assert chapter.content == "My Content"
    assert str(chapter) == "My Title\n\nMy Content"
    assert (
        repr(chapter)
        == "Chapter(filename='123.html', title='My Title', content='My Co')"
    )


@pytest.mark.asyncio()
async def test_extract_chapter_with_html_replace():
    html = """
        <html>
        <head><title>My Title</title></head>
        <body>
            <div id="content">
            &nbsp;&nbsp;&nbsp;&nbsp;Paragraph1
            <br/><br />
            &nbsp;&nbsp;&nbsp;&nbsp;Paragraph2
            <br/>
            <br />
            &nbsp;&nbsp;&nbsp;&nbsp;Paragraph3
            </div>
        </body>
        </html>
    """
    html_replace = [
        ("<br/>", "11"),
        ("<br />", "22"),
        ("&nbsp;&nbsp;", "33"),
    ]
    chapter = await extract_chapter(html, "title", "div#content", html_replace)

    match_regex = r"\n\s+".join(
        [
            "My Title\n\n",
            "3333Paragraph1",
            "1122",
            "3333Paragraph2",
            "11",
            "22",
            "3333Paragraph3",
        ]
    )
    assert re.match(match_regex, str(chapter))


@pytest.mark.asyncio()
async def test_extract_chapter_without_css_path():
    html = """
        <html>
        <head><title>My Title</title></head>
        <body>
            <div id="content">My Content</div>
        </body>
        </html>
    """
    chapter = await extract_chapter(html, None, None)
    assert chapter.title == ""
    assert chapter.content == ""
    assert str(chapter) == ""
    assert repr(chapter) == "Chapter(filename='', title='', content='')"


def test_gen_txt(tmpdir):
    book = Book(
        [
            Chapter("MyTitle1", "MyContent1"),
            Chapter("MyTitle2", "MyContent2"),
        ]
    )

    config = argparse.Namespace(
        **{
            "book_title": "Book Title",
            "book_author": "Book Author",
            "output": str(Path(tmpdir, "book.txt")),
            "txt_replace": (),
        }
    )
    gen_txt(book, config)

    with open(config.output, encoding="utf8") as file:
        content = file.read()
        assert content == (
            "书名：Book Title\n作者：Book Author"
            "\n\nMyTitle1\n\nMyContent1"
            "\n\nMyTitle2\n\nMyContent2"
        )


def test_gen_txt_with_search_and_replace(tmpdir):
    book = Book(
        [
            Chapter("MyTitle1", "MyContent1"),
            Chapter("MyTitle2", "MyContent2"),
        ]
    )

    config = argparse.Namespace(
        **{
            "book_title": "Book Title",
            "book_author": "Book Author",
            "output": str(Path(tmpdir, "book.txt")),
            "txt_replace": [
                ("Title", "TITLE"),
                ("My", "YY"),
            ],
        }
    )
    gen_txt(book, config)

    with open(config.output, encoding="utf8") as file:
        content = file.read()
        assert content == (
            "书名：Book Title\n作者：Book Author"
            "\n\nYYTITLE1\n\nYYContent1\n\nYYTITLE2\n\nYYContent2"
        )


def test_chapter_model_to_str():
    fixture_and_result = [
        (Chapter("MyTitle", "MyContent"), "MyTitle\n\nMyContent"),
        (Chapter("MyTitle", ""), "MyTitle"),
        (Chapter(title="MyTitle"), "MyTitle"),
        (Chapter("", "MyContent"), "MyContent"),
        (Chapter(content="MyContent"), "MyContent"),
        (Chapter(), ""),
    ]
    for fixture, result in fixture_and_result:
        assert str(fixture) == result


def test_search_and_replace_with_invalid_regex(caplog):
    search_and_replace("", [""])
    assert "not enough values to unpack (expected 2, got 0)" in caplog.text
