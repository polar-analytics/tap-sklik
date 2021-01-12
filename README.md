# sklik_el

A Python package to extract and load data from Sklik API

## Install

```bash
pip install -e git+https://github.com/polar-analytics/tap-sklik.git#egg=tap-sklik
```

## Use

Create a `sklik-config.json` file

```json
{ "token": "yourskliktoken" }
```

then run

```bash
tap-sklik -c sklik-config.json
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

### `.env`

Copy `.env.dev` to `.env` and fill any required field.

## Test

```bash
poetry run pytest
```
