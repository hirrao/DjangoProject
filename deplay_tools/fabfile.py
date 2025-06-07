import os
import random
from os.path import exists

from fabric import task

REPO_URL = "https://github.com/hirrao/DjangoProject.git"


@task
def deploy(c):
    user = c.user if hasattr(c, "user") else os.getenv("USER")
    host = c.host
    site_folder = f"/home/{user}/www/{host}"
    source_folder = f"{site_folder}/source"
    _create_directories(c, site_folder)
    _get_latest_source(c, source_folder)


def _create_directories(c, site_folder):
    for subfolder in ("database", "static", "venv", "source"):
        c.run(f"mkdir -p {site_folder}/{subfolder}")


def _get_latest_source(c, source_folder):
    if exists(source_folder + "/.git"):
        c.run(f"cd {source_folder} && git fetch")

    else:
        c.run(f"git clone {REPO_URL} {source_folder}")
    current_commit = c.local("git log -n 1 --format=%H", capture=True)
    c.run(f"cd {source_folder} && git reset --hard {current_commit}")


def _update_settings(c, source_folder, site_name):
    settings_path = source_folder + "/notes/settings.py"
    c.sed(settings_path, "DEBUG = True", "DEBUG = False")
    c.sed(settings_path,
          "ALLOWED_HOSTS =.+$",
          f"ALLOWED_HOSTS = ['{site_name}']"
          )
    secret_key_file = source_folder + "/notes/secret_key.py"
    if not exists(secret_key_file):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)"
        key = "".join(random.SystemRandom().choice(chars) for _ in range(50))
        c.append(secret_key_file, f"SECRET_KEY = '{key}'")
    c.append(settings_path, "\nfrom .secret_key import SECRET_KEY")


def _update_virtualenv(c, source_folder):
    virtualenv_folder = source_folder + "/../venv"
    if not exists(virtualenv_folder + "/bin/pip"):
        c.run(f"python3 -m venv {virtualenv_folder}")
    c.run(f"{virtualenv_folder}/bin/pip install -r {source_folder}/requirements.txt")


def _update_database(c, source_folder):
    c.run(
        f"cd {source_folder}"
        " && ../virtualenv/bin/python manage.py migrate --noinput"
    )
