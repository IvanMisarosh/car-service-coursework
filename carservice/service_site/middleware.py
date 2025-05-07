from django.contrib.messages import get_messages
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.utils.deprecation import MiddlewareMixin


class HtmxMessageMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # if "HX-Request" not in request.headers:
        #     return response

        # if 300 <= response.status_code < 400:
        #     return response

        # if "HX-Redirect" in response.headers:
        #     return response

        # if "text/html" not in response.get("Content-Type", ""):
        #     return response

        # messages = get_messages(request)
        # rendered_messages = render_to_string(
        #     "_toasts.html",
        #     {"messages": messages},
        #     request=request
        # ).strip()

        # if rendered_messages:
        #     response.content += rendered_messages.encode("utf-8")

        return response
