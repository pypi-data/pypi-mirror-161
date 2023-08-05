# Contributing

Setting up development environment:

```bash
python -m pip install --upgrade pip
python -m pip install flit tox
flit install --symlink
```

Show all available tox tasks:

```bash
$ tox -av
...
py37     -> testing against python3.7
py38     -> testing against python3.8
py39     -> testing against python3.9
py310    -> testing against python3.10
lint     -> check code style with flake8 and pylint
cover    -> generate code coverage report in html
doc      -> generate sphinx documentation in html
type     -> check type with mypy
```

To run all tox tasks, we need to install all supported Python version using
[pyenv](https://github.com/pyenv/pyenv):

```bash
pyenv install 3.7.13
pyenv install 3.8.13
pyenv install 3.9.13
pyenv install 3.10.5
```

For code linting, we're using `pre-commit`:

```bash
pre-commit run --all-files
```
