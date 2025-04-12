from abc import ABC, abstractmethod
import selenium
from selenium.webdriver.edge.webdriver import WebDriver


class IWebDriverHandler(ABC):
    @abstractmethod
    def get_driver(self, headless: bool = True) -> WebDriver:
        pass


class WebDriverFactory:
    MS_EDGE = "msedge"
    CHROME = "chrome"
    FIREFOX = "firefox"
    DEFAULT = FIREFOX

    @staticmethod
    def get(browser: str) -> IWebDriverHandler:
        if browser == WebDriverFactory.MS_EDGE:
            return MSEdgeWebDriverHandler()
        elif browser == WebDriverFactory.CHROME:
            return ChromeWebDriverHandler()
        elif browser == WebDriverFactory.FIREFOX:
            return FirefoxWebDriverHandler()
        else:
            raise Exception(f"Unknown browser: {browser}")



class MSEdgeWebDriverHandler(IWebDriverHandler):
    def get_driver(self, headless: bool = True) -> WebDriver:
        from selenium.webdriver.edge.options import Options

        options = Options()
        options.headless = headless

        return selenium.webdriver.Edge(options=options)

# chrome
class ChromeWebDriverHandler(IWebDriverHandler):
    def get_driver(self, headless: bool = True) -> WebDriver:
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.headless = headless

        return selenium.webdriver.Chrome(options=options)

class FirefoxWebDriverHandler(IWebDriverHandler):
    def get_driver(self, headless: bool = True) -> WebDriver:
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from selenium import webdriver

        options = Options()
        options.headless = headless

        return webdriver.Firefox(options=options)
