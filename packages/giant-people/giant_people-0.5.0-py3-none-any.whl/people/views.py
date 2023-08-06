from django.views.generic import ListView

from django.conf import settings

from .models import Person


class PeopleIndex(ListView):
    """
    Index view for People queryset
    """

    model = Person
    context_object_name = "people"
    template_name = "people/index.html"
    paginate_by = getattr(settings, "PEOPLE_PAGINATE_BY", 8)

    def get_queryset(self):
        """
        Override get method here to allow us to access the request user
        """
        return Person.objects.published(user=self.request.user)
