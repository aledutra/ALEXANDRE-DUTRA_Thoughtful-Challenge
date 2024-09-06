from RPA.core.webdriver import download, start
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import logging
import random
from xvfbwrapper import Xvfb

class CustomSelenium:

    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.vdisplay = None

    def start_virtual_display(self):
        """ Start a virtual display to run without headless mode, 
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
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
        return options

    def set_webdriver(self, browser="Chrome"):
        self.start_virtual_display()
        options = self.set_chrome_options()
        executable_driver_path = download(browser)
        self.logger.warning(f"Using downloaded driver: {executable_driver_path}")

        self.driver = start("Chrome", options=options)

        self.driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)

    def set_page_size(self, width:int, height:int):
        #Extract the current window size from the driver
        current_window_size = self.driver.get_window_size()

        #Extract the client window size from the html tag
        html = self.driver.find_element_by_tag_name('html')
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))

        # "Internal width you want to set+Set "outer frame width" to window size
        target_width = width + (current_window_size["width"] - inner_width)
        target_height = height + (current_window_size["height"] - inner_height)
        self.driver.set_window_rect(
            width=target_width,
            height=target_height)

    def open_url(self, url:str, screenshot:str=None):
        print('oppening url')
        self.driver.get(url)
        if screenshot:
            self.driver.get_screenshot_as_file(screenshot)

    def driver_quit(self):
        if self.driver:
            self.driver.quit()