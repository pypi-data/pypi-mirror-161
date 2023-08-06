import argparse
import os
import sys
import traceback
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.wsgi import get_wsgi_application
from django.utils.functional import cached_property
from gunicorn import debug, util
from gunicorn.app.base import Application as BaseApplication
from gunicorn.arbiter import Arbiter
from gunicorn.config import Config as BaseConfig
from gunicorn.config import get_default_config_file, make_settings


class Config(BaseConfig):
    def __init__(self):
        self.settings = make_settings(ignore="pythonpath")
        self.settings[
            "reload"
        ].short = "Restart workers when code changes. Enabled in debug mode."
        self.env_orig = os.environ.copy()

    def add_arguments(self, parser):
        keys = sorted(self.settings, key=self.settings.__getitem__)
        for key in keys:
            self.settings[key].add_option(parser)
        return parser


class Application(BaseApplication):
    def __init__(self, django_command):
        self.django_command = django_command
        self.load_default_config()

    def wsgi(self):
        return get_wsgi_application()

    def load_default_config(self):
        self.cfg = Config()

    def run(self):
        try:
            Arbiter(self).run()
        except RuntimeError as e:
            print("\nError: %s\n" % e, file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)


class Command(BaseCommand):
    help = "Starts a gunicorn web server."

    # Validation is called explicitly each time the server is reloaded.
    requires_system_checks = []
    stealth_options = ("shutdown_message",)
    suppressed_base_arguments = {"--verbosity", "--traceback"}

    @cached_property
    def gunicorn(self):
        return Application(self)

    def add_arguments(self, parser):
        self.gunicorn.cfg.add_arguments(parser)
        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Tells Django to NOT use the auto-reloader in debug mode.",
        )
        parser.add_argument(
            "--skip-checks",
            action="store_true",
            help="Skip Django system checks.",
        )

    def load_gunicorn_config(self):
        # set up import paths and follow symlinks
        self.gunicorn.chdir()

        parser = argparse.ArgumentParser()
        self.gunicorn.cfg.add_arguments(parser)
        env_args = parser.parse_args(self.gunicorn.cfg.get_cmd_args_from_env())

        if self.options["config"]:
            self.gunicorn.load_config_from_file(self.options["config"])
        elif env_args.config:
            self.gunicorn.load_config_from_file(env_args.config)
        else:
            default_config = get_default_config_file()
            if default_config is not None:
                self.gunicorn.load_config_from_file(default_config)

        # Load up environment configuration
        for key, value in vars(env_args).items():
            if value is not None and key in self.gunicorn.cfg.settings:
                self.gunicorn.cfg.set(key.lower(), value)

        # Lastly, update the configuration with any command line settings.
        for key, value in self.options.items():
            if value is not None and key in self.gunicorn.cfg.settings:
                self.gunicorn.cfg.set(key.lower(), value)

        if settings.DEBUG:
            self.gunicorn.cfg.set("post_worker_init", self.post_worker_init)
        self.gunicorn.cfg.set("on_exit", self.on_exit)

        if settings.DEBUG and self.options["use_reloader"]:
            self.gunicorn.cfg.set("reload", True)

        # current directory might be changed by the config now
        # set up import paths and follow symlinks
        self.gunicorn.chdir()

    @staticmethod
    def post_worker_init(worker):
        command = worker.app.django_command

        if not command.options["skip_checks"]:
            command.stdout.write("Performing system checks...\n\n")
            command.check(display_num_errors=True)
        # Need to check migrations here, so can't use the
        # requires_migrations_check attribute.
        command.check_migrations()

        now = datetime.now().strftime("%B %d, %Y - %X")
        command.stdout.write(now)

        quit_command = "CTRL-BREAK" if sys.platform == "win32" else "CONTROL-C"
        command.stdout.write(
            (
                "Django version %(version)s, using settings %(settings)r\n"
                "Quit the server with %(quit_command)s."
            )
            % {
                "version": command.get_version(),
                "settings": settings.SETTINGS_MODULE,
                "quit_command": quit_command,
            }
        )

    @staticmethod
    def on_exit(server):
        command = server.app.django_command
        # 'shutdown_message' is a stealth option.
        shutdown_message = command.options.get("shutdown_message", "")
        if shutdown_message:
            command.stdout.write(shutdown_message)

    def handle(self, *args, **options):
        self.options = options

        if not settings.DEBUG and not settings.ALLOWED_HOSTS:
            raise CommandError("You must set settings.ALLOWED_HOSTS if DEBUG is False.")

        self.load_gunicorn_config()

        if self.gunicorn.cfg.print_config:
            self.stdout.write(str(self.gunicorn.cfg))

        if self.gunicorn.cfg.print_config or self.gunicorn.cfg.check_config:
            try:
                self.gunicorn.wsgi()
            except Exception:
                msg = "\nError while loading the application:\n"
                print(msg, file=sys.stderr)
                traceback.print_exc()
                sys.stderr.flush()
                sys.exit(1)
            sys.exit(0)

        if self.gunicorn.cfg.spew:
            debug.spew()

        if self.gunicorn.cfg.daemon:
            util.daemonize(self.gunicorn.cfg.enable_stdio_inheritance)

        self.gunicorn.run()
