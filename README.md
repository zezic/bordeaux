![Bordeaux](https://raw.github.com/zezic/bordeaux/master/bordeaux-logo.svg?sanitize=true)

# Bordeaux Textboard

Bordeaux is a zero-configuration textboard written in Python. It's potentially vulnerable and created mainly for playing with new async Python framework called [Starlette](https://github.com/encode/starlette).

## Requirements

* Python 3.6+
* [Pipenv](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv)

## Clone and install dependencies

```bash
git clone git@github.com:zezic/bordeaux.git
cd bordeaux
pipenv install
```

## Run

```bash
pipenv run python app.py
```

## Development

Use [mkcert](https://github.com/FiloSottile/mkcert) to generate the certificates:

```bash
mkcert -install
mkcert localhost
```
