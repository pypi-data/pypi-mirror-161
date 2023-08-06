from people import cms_plugins


class TestPeoplePlugin:
    """
    Test case for the People plugin
    """

    def test_template(self):
        """
        Test that the template of the plugin is correct
        """
        plugin = cms_plugins.PersonContainerPlugin()
        assert plugin.render_template == "people/plugin.html"
