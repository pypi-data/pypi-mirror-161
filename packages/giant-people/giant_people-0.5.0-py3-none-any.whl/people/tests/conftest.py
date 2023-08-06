import pytest
from people.models import Person


@pytest.fixture
def person_instance():
    return Person(name="test person", linkedin_url="https://www.linkedin.com/in/testperson")
