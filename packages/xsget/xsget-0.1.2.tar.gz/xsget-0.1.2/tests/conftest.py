# pylint: disable=missing-module-docstring,missing-function-docstring,redefined-outer-name
import pytest


# See https://stackoverflow.com/a/62055409
@pytest.fixture(autouse=True)
def _change_test_dir(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
