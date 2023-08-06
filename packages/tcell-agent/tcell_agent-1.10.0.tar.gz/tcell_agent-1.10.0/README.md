# tCell Python Agent

A tCell.io security agent that instruments your Python web applications.

## Installation

Installing latest agent via pip:

    $ pip install tcell_agent

Install a particular version:

    $ pip install tcell_agent==1.0.1

Install from source:

    $ pip install ~/Downloads/tcellagent_src

Install from a compressed file:

    $ pip install ~/Downloads/pythonagent-tcell-master.zip

## Run application from source

Switch to your project

    $ cd ~/projects/mydjangoapp/

Obtain a `tcell_agent.config` file from the tCell dashboard and place it at the
root of your web app, for this example `~/projects/mydjango/`.

**NOTE!** By default the agent looks for the `tcell_agent.config` in the current
working directory as well as `$TCELL_AGENT_HOME/tcell_agent.config`.

There are two ways you can load the tcell_agent:

### 1. Use the tcell_agent binary to run your app

If you previously started your web app like this:

    $ python manage.py runserver 0.0.0.0:8000

you now start it like this:

    $ tcell_agent run python manage.py runserver 0.0.0.0:8000

### 2. Load the tcell_agent via a wsgi.py file

Assuming your `wsgi.py` (Django) file looks something like this:

```python
import os
from django.core.wsgi import get_wsgi_application
from django_waitlist.settings import PROJECT_ROOT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_waitlist.settings")
application = get_wsgi_application()
```

modify it accordingly:

```python
import os
from django.core.wsgi import get_wsgi_application
from django_waitlist.settings import PROJECT_ROOT

# optional: change default settings via ENV
# os.environ['TCELL_AGENT_CONFIG'] = '/var/www/html/tcell/tcell_agent.config'
# os.environ['TCELL_AGENT_HOME'] = '/var/www/html/tcell'
import tcell_agent
tcell_agent.init()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_waitlist.settings")
application = get_wsgi_application()
```

## Run application from service script

Assuming your service script (`/etc/init.d/myapp.conf`) that looks something
like this:

```sh
script
    set -a
    source /etc/environment
    exec /path/to/bin/uwsgi --ini uwsgi.ini
end script
```

load the tcell_agent by modifying it accordingly:

```sh
script
    set -a
    source /etc/environment
    export TCELL_AGENT_CONFIG='/path/to/tcell-home/tcell_agent.config'
    export TCELL_AGENT_HOME='/path/to/tcell-home/tcell'
    exec /path/to/bin/tcell_agent /path/to/bin/uwsgi --ini uwsgi.ini
end script
```

If you don't want to modify your service script, modifying `wsgi.py` to load the
agent should also work.

## Common pitfalls

* If you're using `tcell_agent` binary, ensure it exists in your path.
* If you're using virtualenv make sure to load the environment before installing
  tcell_agent
* When specifying `TCELL_AGENT_HOME` ensure the app's user has correct
  read/write permissions to that directory.
