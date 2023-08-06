from people.cms_apps import PeopleApp


class TestPeopleApp:
    """
    Test case for the PeopleApp
    """

    def test_get_urls_method(self):
        """
        Test get_urls method on the PeopleApp class
        """
        assert PeopleApp().get_urls() == ["people.urls"]
