# tap-sklik

A [Singer tap](https://www.singer.io/) to extract data from the [Sklik API](https://api.sklik.cz/).

## Install

```bash
pip install -e git+https://github.com/polar-analytics/tap-sklik.git#egg=tap-sklik
```

## Use

Create a `sklik-config.json` file

```json
{ "token": "yourskliktoken", "start_date": "YYYYmmdd", "end_date": "YYYYmmdd" }
```

then run

```bash
tap-sklik -c sklik-config.json
```

more help

```bash
tap-sklik -c sklik-config.json --help
```

## Development

### Tools

Install poetry

```bash
poetry env use 3.8
poetry install
```

It will create a `./.venv` virtual env that you can use for development.

> Note: a standardized `.vscode` config is provided.

> Note: the project follows `black` codestyle, and lints with `flake8`

### Environment variables

Copy `.env.dev` to `.env` and fill any required field.

## Test

```bash
poetry run pytest
```
