from RPA.core.webdriver import download, start
from selenium import webdriver
import logging

class CustomSelenium:

    def __init__(self):
        self.driver = None
        self.logger = logging.getLogger(__name__)

    def set_chrome_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1420,1080')
        options.add_argument('--headless')
        options.add_argument("--disable-gpu")
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-webgpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("--disable-extensions")
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')

        # options.add_argument("--start-maximized")
        # options.add_argument('--remote-debugging-port=9222')
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return options

    def set_webdriver(self, browser="Chrome"):
        options = self.set_chrome_options()
        executable_driver_path = ''
        if not executable_driver_path:
            executable_driver_path = download(browser)
            message = executable_driver_path
            self.logger.warning("Using downloaded driver: %s" % executable_driver_path)
        else:
            self.logger.warning("Using cached driver: %s" % executable_driver_path)

        self.driver = start("Chrome", options=options)

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