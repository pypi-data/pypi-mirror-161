# Moose Frank

A Python package packed with tools that are commonly used in Moose projects.


## Development

See the [CONTRIBUTING](CONTRIBUTING.md) guide.


## Installation

```console
pip install moose-frank
```


## Local testing

isort

```console
docker-compose run --rm --no-deps python isort [module/path] [options]
```

---

flake8

```console
docker-compose run --rm --no-deps python flake8 [module/path]
```

---

black

```console
docker-compose run --rm --no-deps python black [module/path]
```

---

pytest

```console
docker-compose run --rm --no-deps python coverage run ./runtests.py
```


## Translations

Updating translations

```console
docker-compose run --rm --no-deps manage makemessages -l nl --no-wrap --no-location --no-obsolete
docker-compose run --rm --no-deps manage compilemessages
```


## Google Cloud storage retry patch

Add the following to your main django app to apply the patch.

```python
from django.apps import AppConfig
from moose_frank.storages.gcloud_retry_patch import apply_gcloud_retry_patch


class MainConfig(AppConfig):
    def ready(self) -> None:
        super().ready()
        apply_gcloud_retry_patch()
```

In case you need te revert this patch you can call `moose_frank.storages.gcloud_retry_patch.revert_gcloud_retry_patch`.
