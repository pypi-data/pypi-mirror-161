from clicknium.core.models.web.basewebdriver import BaseWebDriver
from clicknium.core.models.web.webextension import WebExtension


class WebDriver(BaseWebDriver):

    def __init__(self, browser_type):
        super(WebDriver, self).__init__(browser_type)                  
        self.extension = WebExtension(browser_type)