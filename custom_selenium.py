import logging

from RPA.core.webdriver import download, start
from selenium.webdriver.chrome.options import Options
from xvfbwrapper import Xvfb


class CustomSelenium:

    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.vdisplay = None

    def start_virtual_display(self):
        """Start a virtual display to run without headless mode,
        because the site are blockig due bot activity.
        """
        self.vdisplay = Xvfb(width=1920, height=1080)
        self.vdisplay.start()
        self.logger.info("Virtual display started")

    def stop_virtual_display(self):
        if self.vdisplay:
            self.vdisplay.stop()
            self.logger.info("Virtual display stopped")

    def set_chrome_options(self):
        options = Options()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        )
        return options

    def set_webdriver(self, browser="Chrome"):
        self.start_virtual_display()
        options = self.set_chrome_options()
        executable_driver_path = download(browser)
        self.logger.warning(f"Using downloaded driver: {executable_driver_path}")

        self.driver = start("Chrome", options=options)

        self.driver.execute_script(
            """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """
        )

    def driver_quit(self):
        if self.driver:
            self.driver.quit()
