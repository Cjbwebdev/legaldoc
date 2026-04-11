from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView

def health(request):
    return HttpResponse("ok")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/", include("users.urls", namespace="users")),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain"), name="robots"),
    path("sitemap.xml", TemplateView.as_view(template_name="sitemap.xml", content_type="application/xml"), name="sitemap"),
    path("_health/", health, name="health"),
    path("", include("billing.urls", namespace="billing")),
    path("", include("dashboard.urls", namespace="dashboard")),
]
