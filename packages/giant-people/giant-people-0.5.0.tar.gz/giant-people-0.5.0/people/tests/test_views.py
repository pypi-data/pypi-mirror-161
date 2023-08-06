from django.test import Client
from django.urls import reverse

import pytest

from .conftest import *


@pytest.mark.django_db
class TestIndexView:
    """
    Test case for the People app views
    """

    def test_people_index(self):
        """
        Test the index view returns the correct status code
        """
        client = Client()
        response = client.get(reverse("people:index"))
        assert response.status_code == 200
