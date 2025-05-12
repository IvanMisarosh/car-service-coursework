from django.contrib.messages import get_messages
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin
import json
from django.contrib import messages


class HtmxMessageMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        hx_trigger = response.headers.get('HX-Trigger')
        if hx_trigger is None:
            hx_trigger = {}
        elif hx_trigger.startswith("{"):
            hx_trigger = json.loads(hx_trigger)
        else:
            hx_trigger = {hx_trigger: True}

        hx_trigger['messages'] =  [
                {
                    'message': message.message,
                    'tags': message.tags
                }
                for message in messages.get_messages(request)
            ]
        
        response.headers["HX-Trigger"] = json.dumps(hx_trigger)

        return response
