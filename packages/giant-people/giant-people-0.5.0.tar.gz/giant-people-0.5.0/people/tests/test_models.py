import pytest
from people.models import Person


@pytest.mark.django_db
class TestPersonModel:
    def test_published(self, person_instance):
        person_instance.is_published = True
        person_instance.save()
        assert Person.objects.published().count() == 1

    def test_unpublished(self, person_instance):
        person_instance.save()
        assert Person.objects.count() == 1
        assert Person.objects.published().count() == 0

    def test_quote(self, person_instance):
        person_instance.quote = '"This is something I say"'
        person_instance.save()
        assert Person.objects.count() == 1
        person = Person.objects.first()
        assert person.quote == '"This is something I say"'
