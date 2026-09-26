# Django template

Provisioned from [`Qode-Platform/fleet-template-v1`](https://github.com/Qode-Platform/fleet-template-v1) — the fleet
lifecycle contract (`bin/`, `fleet.conf`, deploy workflows) with a
Django starter laid on top.

## Origin

    django-admin startproject config + django-admin startapp core (Django 6.1.1)

Generated 2026-09-21 on Node v22.12.0 / Python 3.12.3. **Dependencies were
never installed and this has never been built or run.** Boot it once before
trusting it.

## Fleet lifecycle

`fleet.conf` drives every script in `bin/`:

| step | command |
|---|---|
| install | `python3 -m venv .venv && .venv/bin/pip install --upgrade pip -r requirements.txt` |
| build | `.venv/bin/python manage.py migrate --noinput` |
| start | `.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |

    ./bin/run       # install, build, start in the foreground
    ./bin/start     # start from existing build artifacts
    ./bin/restart   # rebuild and restart
    ./bin/stop      # stop whatever holds the port

Listens on `$PORT` (default `8000`); health check hits `/`.

## Serving

The fleet injects `PORT` and `DATABASE_URL`; the app is served at the root of its
own hostname (`https://<hash>.<FLEET_APP_DOMAIN>/`), so every route, redirect and
asset URL is a plain root path.

- ALLOWED_HOSTS now reads $DJANGO_ALLOWED_HOSTS (default `*`) — with the stock empty list Django 400s behind the ingress.

## What differs from stock output

- Added requirements.txt (Django, gunicorn) — startproject does not generate one.
- settings.py is untouched CLI output: DEBUG=True and ALLOWED_HOSTS=[] . Set ALLOWED_HOSTS before any real deploy.
