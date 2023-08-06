from django.core.validators import URLValidator
from django.db import models
from cms.models import CMSPlugin

from filer.fields.image import FilerImageField

from mixins.models import PublishingMixin, PublishingQuerySetMixin, TimestampMixin


class PersonAbstract(models.Model):
    """
    Represents a person object
    """

    name = models.CharField(max_length=255)
    job_role = models.CharField(max_length=255, blank=True)
    image = FilerImageField(related_name="person_image", null=True, on_delete=models.SET_NULL)
    quote = models.TextField(
        blank=True,
        help_text="Optional. A single paragraph. Quotation marks need to be added if intended",
    )
    summary = models.TextField(blank=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Set this to prioritise the order of the person, higher numbers are higher priority",  # noqa
    )
    # Contact/social details
    linkedin_url = models.URLField(
        help_text="Enter the full URL of the LinkedIn page",
        blank=True,
        validators=[
            URLValidator(
                schemes=["https"],
                regex="www.linkedin.com",
                message="Please enter the full URL of the LinkedIn page",
            )
        ],
    )
    phone_number = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        """
        Return string representation
        """
        return self.name


class Person(TimestampMixin, PublishingMixin, PersonAbstract):

    objects = PublishingQuerySetMixin.as_manager()

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["-order", "name"]


class PersonContainer(CMSPlugin):
    """
    Represents a selection of people relevant to the page.
    """

    def copy_relations(self, oldinstance):
        """
        Copy the relations from oldinstance and update the plugin field
        """
        self.people_cards.all().delete()
        for item in oldinstance.people_cards.all():
            item.pk = None
            item.plugin = self
            item.save()

    def __str__(self):
        """
        String representation of the model object
        """
        return f"People Container {self.pk}"


class PersonCard(models.Model):
    """
    Acts as a bridge between the people app and the people container plugin to allow for custom ordering
    """

    person = models.ForeignKey(to=Person, related_name="people_cards", on_delete=models.CASCADE)
    plugin = models.ForeignKey(
        to=PersonContainer, on_delete=models.CASCADE, related_name="people_cards"
    )
    card_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("card_order",)

    def __str__(self):
        """
        String representation of the object
        """
        return f"Person card for {self.person.name}"
