from fabric.contrib.files import append, exists, sed
from fabric.api import cd, env, local, run
import random

REPO_URL = 'https://github.com/zacherytapp/superlists.git'

def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run('git clone %s .' % REPO_URL)
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('git reset --hard %s' % current_commit)

def _update_settings(site_name):
    settings_path = 'superlists/settings.py'
    sed(settings_path, "DEBUG = TRUE", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % site_name
    )
    secret_key_file = 'superlists/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, 'SECRET_KEY = "%s"' % key)
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv():
    if not exists('virtualenv/bin/pip3'):
        run('python3 -m venv virtualenv')
    run('./virtualenv/bin/pip3 install -r requirements.txt')

def _update_static_files():
    run('./virtualenv/bin/python3 manage.py collectstatic --noinput')

def _update_database():
    run('./virtualenv/bin/python3 manage.py migrate --noinput')

def deploy():
    site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    run('mkdir -p %s' % site_folder)
    with cd(site_folder):
        _get_latest_source()
        _update_settings(env.host)
        _update_virtualenv()
        _update_static_files()
        _update_database()

def _create_local_user():
    sudo('apt-get update')
    sudo('apt-get upgrade -y')
    sudo('apt-get fail2ban')
    run('adduser deploy')
    run('usermode -aG sudo deploy')

def setup_server():
    pass
