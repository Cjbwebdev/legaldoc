from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse

def health(request):
    return HttpResponse("ok")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("_health/", health, name="health"),
    path("", include("billing.urls", namespace="billing")),
    path("", include("dashboard.urls", namespace="dashboard")),
]
