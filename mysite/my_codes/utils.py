from django.http import JsonResponse


class ApiHttpResponse(JsonResponse):
    def __init__(self, *, status, error_message=None, body=None):
        is_error_status = False if 200 <= status <= 299 else True

        if is_error_status:
            json = {
                "type": "error",
                "error": (
                    error_message
                    if error_message is not None
                    else "Error message undefined."
                ),
            }
        else:
            json = body if body is not None else {}
            json["type"] = "success"

        json["status"] = status

        super().__init__(json, status=status)


def create_post(user, text, files):
    return False
    return True
