"""Billing URLs — LegalDoc"""
from django.urls import path
from django.views.generic import TemplateView

app_name = 'billing'
urlpatterns = [
    path("billing/", TemplateView.as_view(template_name="billing.html"), name="billing"),
]
