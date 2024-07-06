# middlewares.py

from django.http import JsonResponse

class LimitUploadSizeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        max_upload_size = 2.5 * 1024 * 1024  # 2.5 MB

        if request.method in ['POST', 'PUT'] and request.FILES:
            for _, file in request.FILES.items():
                if file.size > max_upload_size:
                    return JsonResponse(
                        {"detail": f"File size should not exceed {max_upload_size / (1024 * 1024)} MB."},
                        status=413
                    )
        
        response = self.get_response(request)
        return response
