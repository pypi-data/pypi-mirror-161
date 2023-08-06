### ExeceptionMiddeware

Exception to teams middleware is a simple django app that
contains only a middelware that is resposible for sending logs
to your teams channel using webhook in any event of internal server error.

[How to create webhook for teams channel](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook)


### Tools

- [Django 3.2.12](https://djangoproject.com)

### Installation

On your terminal/shell

```bash

pip3 install exeception-to-teams

```

### Quiz setup

---

In your project's settings.py file. Add exeception_to_teams in your `INTALLLED_APPS` list, configure middleware as following. You must define `TEAMS_CHANNEL_URL`

```python
# settings.py

INSTALLED_APPS = [
  ...,
  "exeception_to_teams",
]


MIDDLEWARES =[
...
'exeception_to_teams.middlewares.ExeceptionMiddleware'
]

TEAMS_CHANNEL_URL = os.envion.get("TEAMS_CHANNEL_URL")

PROJECT_NAME = "Project X" # Uses this value in card title.
```

Generate an exeception intentionally in your django application and check log in your teams channel.

**Have a great day!**