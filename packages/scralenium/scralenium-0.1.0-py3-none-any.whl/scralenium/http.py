"""
Module containing the custom request and response subclasses.

These objects are subclasses of Scrapy's Request and TextResponse
objects and add features for controlling the Selenium WebDriver.
"""

from scrapy import Request
from scrapy.http import TextResponse


class ScraleniumRequest(Request):
    """
    ScraleniumRequest is a subclass of scrapy request object.

    Super Class
    -----------
    Request : scrapy.Request
        the built in scrapy request object
    """

    def __init__(
        self,
        *args,
        pause=None,
        screenshot=False,
        screenshot_count=None,
        screenshot_duration=None,
        script=None,
        **kwargs
    ):
        """
        Construct for the ScraleniumRequest object class.

        Parameters
        ----------
        pause : int, optional
            number of seconds, by default None
        screenshot : bool, optional
            webdriver should capture screenshot, by default False
        screenshot_count : int, optional
            the number of screenshots, by default None
        screenshot_duration : int, optional
            number of seconds in between screenshots, by default None
        script : str, optional
            javescript script source, by default None
        """
        self.pause = pause
        self.screenshot = screenshot
        self.screenshot_count = screenshot_count
        self.screenshot_duration = screenshot_duration
        self.script = script
        super().__init__(*args, **kwargs)


class ScraleniumResponse(TextResponse):
    """
    ScraleniumResponse is a subclass from scrapy.Response.

    Super Class
    -----------
    TextResponse : scrapy.TextResponse
        The default TextResponse used by scrapy
    """

    def __init__(self, driver, *args, images=None, **kwargs):
        """
        Construct for the ScraleniumResponse object.

        Parameters
        ----------
        driver : selenium.webdriver.RemoteDriver
            the webdriver class for browser contorl.
        images : Images, optional
            screenshots captured by the webdriver, by default None
        """
        self.__driver = driver
        self.images = images
        super().__init__(*args, **kwargs)

    def __getattr__(self, attr):
        """
        Grab attribute from the webdriver if not on the response.

        Parameters
        ----------
        attr : str
            the attribute requested by user.

        Returns
        -------
        Object
            attribute object bound to webdrives.
        """
        if hasattr(self.driver, attr):
            return getattr(self.driver, attr)
        raise AttributeError

    @property
    def driver(self):
        """
        Return selenium webdriver browser controller.

        Returns
        -------
        Object
            The webdriver
        """
        return self.__driver
