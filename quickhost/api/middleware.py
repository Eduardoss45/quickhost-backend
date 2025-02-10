import uuid
from django.http import JsonResponse


class UUIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "user/accommodation/create/" in request.path:
            try:
                id_user = request.path.split("/")[-2]
                uuid.UUID(str(id_user))
            except (ValueError, IndexError):
                return JsonResponse(
                    {"error": "O ID fornecido não corresponde ao formato UUID."},
                    status=400,
                )
        response = self.get_response(request)
        return response
