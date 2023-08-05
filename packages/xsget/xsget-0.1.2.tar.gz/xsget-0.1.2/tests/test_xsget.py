# pylint: disable=missing-module-docstring,missing-function-docstring

import argparse
from shlex import split as argv

from xsget import __version__
from xsget.xsget import (
    extract_urls,
    http_headers,
    is_relative_url,
    url_to_filename,
)

DEFAULT_URL = "http://localhost"


def test_required_url(script_runner):
    ret = script_runner.run(*argv("xsget"))
    assert (
        "xsget: error: the following arguments are required: URL" in ret.stderr
    )


def test_generating_default_config_file(script_runner):
    ret = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    assert "Create config file: xsget.toml" in ret.stdout
    assert (
        "Cannot connect to host localhost:80 "
        "ssl:default [Connect call failed ('127.0.0.1', 80)]" in ret.stdout
    )


def test_generating_default_config_file_with_existing_found(script_runner):
    _ = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    ret = script_runner.run(*argv(f"xsget {DEFAULT_URL} -g"))
    assert "Existing config file found: xsget.toml" in ret.stdout


def test_version(script_runner):
    ret = script_runner.run(*argv("xsget -v"))
    assert f"xsget {__version__}" in ret.stdout


def test_url_to_filename():
    expected = [
        ("http://a.com/123", "123.html"),
        ("http://a.com/123/456", "456.html"),
        ("http://a.com/123/456/789", "789.html"),
        ("http://a.com/123.html", "123.html"),
    ]
    for url, filename in expected:
        assert url_to_filename(url) == filename

    expected = [
        ("http://a.com/123?id=aaa", "id", "aaa.html"),
        ("http://a.com/456.php?tid=abc", "tid", "abc.html"),
    ]
    for url, url_param, filename in expected:
        assert url_to_filename(url, url_param) == filename


def test_is_relative_url():
    expected = [
        ("http://a.com/123", False),
        ("//a.com/123/456", True),
        ("/123/456.html", True),
    ]
    for url, result in expected:
        assert is_relative_url(url) == result


def test_extract_urls():
    html = """
        <html>
        <body>
        <div class="toc">
            <a href="http://a.com/123"/>a</a>
            <a href="http://a.com/123/789.html"/>b</a>
            <a href="//a.com/987"/>c</a>
            <a href="/123/456"/>d</a>
            <a href="/123/654.html"/>e</a>
        </div>
        </body>
        </html>
    """

    expected_urls = [
        "http://a.com/123",
        "http://a.com/123/789.html",
        "http://a.com/987",
        "http://a.com/123/456",
        "http://a.com/123/654.html",
    ]

    css_paths = [
        "html body div.toc a",
        "html body div a",
        "body div.toc a",
        "div.toc a",
        "div a",
        "a",
    ]
    for css_path in css_paths:
        config = argparse.Namespace(
            base_url="http://a.com/123", link_css_path=css_path
        )
        assert extract_urls(html, config) == expected_urls


def test_user_agent():
    user_agent = http_headers()["User-Agent"]
    assert "Mozilla/5.0" in user_agent
