"""Module contains the middleware controller for Scralenium Middleware."""

import time

from scrapy import signals
from selenium import webdriver

from scralenium.http import ScraleniumRequest, ScraleniumResponse

DRIVERS = {
    "chrome": webdriver.Chrome,
    "firefox": webdriver.Firefox,
    "remote": webdriver.Remote,
}


class ScraleniumDownloaderMiddleware:
    """
    Middleware for controling initiating the webdriver.
    """

    @classmethod
    def from_crawler(cls, crawler):
        """
        Create the middleware instance.

        Parameters
        ----------
        crawler : scrapy.Crawler
            the url crawler process.

        Returns
        -------
        ScraleniumDownloaderMiddleware
            instance of this class
        """
        executable = crawler.settings.get("SELENIUM_DRIVER_EXECUTABLE")
        name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        s = cls(executable, name)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def __init__(self, executable, name):
        """
        Construct the ScraleniumDownloaderMiddleware class.

        Parameters
        ----------
        executable : str
            path to webdriver executable.
        name : str
            the name of the browser.
        """
        self.executable = executable
        self.name = name
        self._driver = None
        self.images = []

    @property
    def driver(self):
        """
        Create and return selenium webdriver object.

        Returns
        -------
        selenium.WebDriver
            the webdriver browser controller.
        """
        if not self._driver:
            if not self.name:
                self.name = "chrome"
            driverclass = DRIVERS[self.name]
            if self.executable:
                self._driver = driverclass(self.executable)
            else:
                self._driver = driverclass()
        return self._driver

    def _set_user_agent(self, driver, request, spider):
        """
        Set the user agent for the webdriver.

        Parameters
        ----------
        driver : selenium.WebDriver
            the web driver.
        request : ScraleniumRequest
            the request being processed
        spider : scrapy.Spider
            the current spider class.
        """
        try:
            user_agent = request.headers["User-Agent"].decode("utf-8")
            if "scrapy" in user_agent:
                return
            driver.execute_cdp_cmd(
                "Network.setUserAgentOverride", {"userAgent": user_agent}
            )
        except KeyError:
            spider.logger.info("Couldn't apply User Agent.")

    def process_request(self, request, spider):
        """
        Process the current request.

        Parameters
        ----------
        request : ScraleniumRequest
            the current request
        spider : scrapy.Spider
            the current spider in use.

        Returns
        -------
        ScraleniumResponse
            the response created from the request received.
        """
        if isinstance(request, ScraleniumRequest):
            driver = self.driver
            self._set_user_agent(driver, request, spider)
            driver.get(request.url)
            for name, value in request.cookies.items():
                driver.add_cookie({"name": name, "value": value})
            if request.pause:
                spider.logger.info("Implicitly Waiting...")
                driver.implicitly_wait(request.pause)
            if request.script:
                spider.logger.info("Runnin Script...")
                driver.execute_script(request.script)
            if request.screenshot:
                spider.logger.info("Making Screenshot(s)...")
                if request.screenshot_count:
                    self._screenshots(
                        request.screenshot_count, request.screenshot_duration
                    )
                else:
                    self._screenshot()
            request.images = self.images
            body = driver.page_source
            response = ScraleniumResponse(
                driver,
                driver.current_url,
                images=self.images,
                request=request,
                body=body.encode("utf-8"),
                encoding="utf-8",
            )
            return response
        return None

    def _screenshot(self):
        """
        Take screenshot of webpage.
        """
        image = self.driver.get_screenshot_as_png()
        self.images.append(image)

    def _screenshots(self, qty, duration):
        """
        Take screenshots of webpage.

        Parameters
        ----------
        qty : int
            number of screenshots
        duration : int
            time in between screenshots
        """
        for _ in range(qty - 1):
            self._screenshot()
            time.sleep(duration)
        self._screenshot()

    def spider_closed(self, spider):
        """
        Close the spider and the webdriver.

        Parameters
        ----------
        spider : scrapy.Spider
            the current spider in use.
        """
        spider.logger.info(f"Spider opened: {spider.name}")
        self.driver.quit()
