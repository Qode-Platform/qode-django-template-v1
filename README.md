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

## BASE_PATH

The fleet injects `BASE_PATH` (`/direct/<agent>:<port>`) and nginx forwards
that prefix **unchanged** — so this app serves every route and asset under
it. An empty or unset value means standalone mode: serve at the host root.

- A WSGI wrapper in config/wsgi.py moves the prefix into SCRIPT_NAME; FORCE_SCRIPT_NAME makes reverse() emit it.
- `HEALTH_PATH` in `fleet.conf` stays un-prefixed; the fleet prepends `$BASE_PATH` itself.
- A value like `direct/x:3000/` is normalised to `/direct/x:3000`.
- ALLOWED_HOSTS now reads $DJANGO_ALLOWED_HOSTS (default `*`) — with the stock empty list Django 400s behind the ingress.
- Verified here: a GET to <prefix>/admin/ resolves and its redirect carries the prefix.
- Django stays lenient — it also answers at the bare root. FastAPI and Flask 404 there.

## What differs from stock output

- Added requirements.txt (Django, gunicorn) — startproject does not generate one.
- settings.py is untouched CLI output: DEBUG=True and ALLOWED_HOSTS=[] . Set ALLOWED_HOSTS before any real deploy.

## Rule: everything under BASE_PATH

The fleet serves this app behind a proxy at `BASE_PATH=/direct/<agent>:<port>`, and the
prefix is forwarded **unchanged** — it is NOT stripped before it reaches Django. So every
route, every redirect, every asset URL and every docs URL the app emits must carry
`$BASE_PATH`.

Never hard-code a leading-slash path in a template, a view, or a redirect. `href="/about/"`,
`redirect("/login/")` and `src="/static/app.css"` all point at the proxy's root and 404.

Use Django's own mechanism — it already does this for you here:

- `config/settings.py` sets `FORCE_SCRIPT_NAME` and `STATIC_URL` from `$BASE_PATH`;
  `config/wsgi.py` moves the prefix out of `PATH_INFO` into `SCRIPT_NAME`.
- In templates use `{% url 'name' %}` and `{% static 'app.css' %}`; in Python use
  `reverse()` / `redirect('name')`. All of them emit the prefix automatically.
- `HEALTH_PATH` in `fleet.conf` stays un-prefixed; the fleet prepends `$BASE_PATH` itself.
