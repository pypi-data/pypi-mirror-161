from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool


@apphook_pool.register
class PeopleApp(CMSApp):
    """
    App hook for People app
    """

    app_name = "people"
    name = "People"

    def get_urls(self, page=None, language=None, **kwargs):
        """
        Return the path to the apps urls module
        """

        return ["people.urls"]
