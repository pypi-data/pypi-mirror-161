# sparta-memcached

Sparta memcached library.

## Usage

See [here](/USAGE.md).

## Dependency management

You need to have [virtualenv](https://docs.python.org/3/tutorial/venv.html) installed globally. In case you don't, run:

```bash
pip install virtualenv
```

Create and activate a **_virtualenv_** (name it `.venv`).

```bash
python -m venv .venv
source .venv/bin/activate
```

> You should now see the prefix `(.venv)` in your terminal prompt. This means the virtualenv is active.

## Install locally

Install default and test requirements (assure `.venv` is active).

```shell
pip install -e .[test]
```

> If it's the first time you install, you may need to [Setup Google Artifact Registry](#Setup-Google-Artifact-Registry)

Run tests.

```shell
python -m pytest
```

## Publish on [Pypi](https://pypi.org/project/sparta-memcached/)

Publish to [pypi.org](https://pypi.org/project/sparta-memcached/).

A cloud build will deploy the package whenever a new tag is pushed to pur git repo.

```shell
./scripts/rollout_version.sh [patch|minor|major]
```

> When prompt `Push changes?`, type `y`.

Alternatively, you can publish manually.

```shell
./scripts/publish.sh --username spartanaproach --password ***
```
