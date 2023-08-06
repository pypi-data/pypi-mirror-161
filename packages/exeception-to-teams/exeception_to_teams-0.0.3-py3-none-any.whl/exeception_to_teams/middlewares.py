"""Exception to teams middleware is a simple django app that
contains only a middelware that is resposible for sending logs
to your teams channel in an event of any internal server error.
"""

import datetime
import json
import logging
import os
import sys
import traceback

import requests
from django.conf import settings

try:
    TEAMS_CHANNEL_URL = settings.TEAMS_CHANNEL_URL
except AttributeError as e:
    raise AttributeError("You must define 'TEAMS_CHANNEL_URL' in your settings") from e

try:
    PROJECT_NAME = settings.PROJECT_NAME
except AttributeError as e:
    PROJECT_NAME = "Django Project"

class ExeceptionMiddleware:
    """Add this middleware in your middleware's list
    to send any internal server error logs to your teams channel.
    You must define 'TEAMS_CHANNEL_URL' in your settings.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def process_exception(self, request, _exception):
        """fyi: django runs this function when an exception occurs."""
        payload = self.prepare_exception(request)
        self.send_logs_to_channel(*payload, exception=str(_exception))

    @staticmethod
    def prepare_exception(request):
        """this method formats exception."""
        traceback_ = sys.exc_info()[2]
        formated_tb = traceback.format_tb(traceback_)
        message = (
            json.dumps(formated_tb)
            .replace("\\n", "<br/>")
            .replace('"', "")
            .replace("[", "")
            .replace("]", "")
            .replace("\/", "/")
            .replace("\\", "")
            .replace(",   ", "")
        )
        user = {"username": "Anynomous", "image": "https://itsmilann.com/cat.png"}
        if request.user.is_authenticated:
            user = {
                "username": request.user.username,
                "image": "https://itsmilann.com/cat.png",
            }
        formatted_payload = None
        payload = {
            "method": request.method,
            "path": request.path,
            "params": f"```json\n{json.dumps(request.GET)}",
            "payload": f"```json\n{formatted_payload}",
            "remote_address": request.META.get("REMOTE_ADDR", "Not Found"),
            "user_agent": request.META.get("HTTP_USER_AGENT", "Not Found"),
            "headers": {},
        }
        return message, user, payload

    @staticmethod
    def send_logs_to_channel(traceback_, user, payload, exception=None):
        """this method send formatted logs to channel"""
        headers = {"content-type": "application/json;charset=UTF-8"}
        if exception is None:
            exception = "Internal Server Error"
        data = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "title": f"An Exception Occurred in {PROJECT_NAME}",
            "summary": f"An Exception Occurred in {PROJECT_NAME}",
            "sections": [
                {
                    "activityTitle": f"{user['username']}",
                    "activitySubtitle": f'{payload["method"]}: {payload["path"]}',
                    "activityImage": user["image"],
                    "facts": [
                        {"name": "", "value": f"<h4>{exception}</h4>"},
                        {"name": "Payload", "value": f'{payload["payload"]}'},
                        {"name": "Parameters", "value": f'{payload["params"]}'},
                        {
                            "name": "Remote Address",
                            "value": f'{payload["remote_address"]}',
                        },
                        {"name": "User Agent", "value": f'{payload["user_agent"]}'},
                        {
                            "name": "Created Date",
                            "value": str(datetime.datetime.now()),
                        },
                        {
                            "name": "Traceback",
                            "value": f"<hr/><code sytle='white-space: pre-wrap'>{traceback_} </code><hr/>",
                        },
                    ],
                    "markdown": True,
                }
            ],
            "potentialAction": [],
        }
        data = json.dumps(data)
        uri = os.environ.get("TEAMS_CHANNEL_URL", TEAMS_CHANNEL_URL)
        res = requests.post(url=uri, data=data, headers=headers)
        if res.status_code not in range(200, 300):
            timestamp = datetime.datetime.now()
            # pylint:disable=consider-using-f-string
            err = (
                "An exception occured in our backend service at %s but failed send log to channel."
                % timestamp
            )
            logging.critical(err)

    def __call__(self, request):
        response = self.get_response(request)
        return response
