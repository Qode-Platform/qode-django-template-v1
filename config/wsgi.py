"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()


class BasePathMiddleware:
    """Serve the app under the fleet's ingress prefix.

    nginx forwards `/direct/<agent>:<port>` UNCHANGED, so PATH_INFO arrives
    carrying the prefix. WSGI's own convention is that the mount point lives in
    SCRIPT_NAME and PATH_INFO is relative to it — so move it across, and
    Django's resolver and FORCE_SCRIPT_NAME do the rest. No prefix configured
    means this is a pass-through.
    """

    def __init__(self, app, prefix: str) -> None:
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if self.prefix:
            path = environ.get("PATH_INFO", "")
            if path == self.prefix or path.startswith(self.prefix + "/"):
                environ["SCRIPT_NAME"] = self.prefix
                environ["PATH_INFO"] = path[len(self.prefix):] or "/"
        return self.app(environ, start_response)


_raw = (os.environ.get("BASE_PATH") or "").strip().strip("/")
application = BasePathMiddleware(application, f"/{_raw}" if _raw else "")
