from django.http import JsonResponse

# Create your views here.
def health(_request):
    return JsonResponse({"status": "ok", "service": "paypulse-backend"}, status=200)

