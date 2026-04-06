"""
Custome Exceptions Handler

{"Error": true, "Msg": "....", "Details":{.....}}

"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    # Normalise the response body
    original_data = response.data
    message = "Request failed."
    if isinstance(original_data, dict):
    # Pull out a top-level "detail" if DRF put one there
        message = original_data.pop("detail", message)
        if hasattr(message, "code"): # AuthenticationFailed et
            message = str(message)
        details = original_data if original_data else {}
    elif isinstance(original_data, list):(
        details) = {"non_field_errors": original_data}
    else:
        details = {}

    response.data = {
        "error": True,
        "message": str(message),
        "details": details,
    }
    return response