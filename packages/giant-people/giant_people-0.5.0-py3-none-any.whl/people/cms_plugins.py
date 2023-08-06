from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin

from . import models


class PersonCardInline(SortableInlineAdminMixin, admin.TabularInline):
    """
    People selection inline.
    """

    model = models.PersonCard
    extra = 1


@plugin_pool.register_plugin
class PersonContainerPlugin(CMSPluginBase):
    """
    Plugin for the PersonContainer plugin.
    """

    render_template = "people/plugin.html"
    name = "People Block"
    model = models.PersonContainer

    inlines = [PersonCardInline]
