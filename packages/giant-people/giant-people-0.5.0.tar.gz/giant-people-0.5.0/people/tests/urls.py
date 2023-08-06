from django.urls import include, path

""""
Url patterns for testing
"""

urlpatterns = [path("people/", include("people.urls", namespace="people"))]
