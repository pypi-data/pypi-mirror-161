from django.urls import path

from .views import PeopleIndex

app_name = "people"

urlpatterns = [
    path("", PeopleIndex.as_view(), name="index"),
]
