import os
import re
import time
import glob
import logging
import urllib.parse
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# Define logger
logger = logging.getLogger(__name__)

class News:
    """
    Represents a news item with various attributes and parsing methods.
    """

    def __init__(self, web_element: WebElement, search_phrase: str):
        """
        Initialize a News object.

        Args:
            web_element (WebElement): The web element containing the news item.
            search_phrase (str): The phrase used to search for news.
        """
        self.web_element = web_element
        self.search_phrase = search_phrase
        self.image_link: Optional[str] = None
        self.image_name: Optional[str] = None
        self.date: Optional[datetime] = None
        self.title: Optional[str] = None
        self.count_phrase: Optional[str] = None
        self.contain_money: Optional[bool] = None

    def parse_title(self) -> None:
        """Parse and set the title of the news item."""
        try:
            self.title = self.web_element.find_element(By.CSS_SELECTOR, '[data-testid="Heading"]').text
            logger.info(f"Parsed title: {self.title}")
        except NoSuchElementException:
            logger.error("Failed to parse title: Element not found")
            self.title = None

    def parse_date(self) -> None:
        """Parse and set the date of the news item."""
        try:
            date_elem = self.web_element.find_element(By.CSS_SELECTOR, 'time[data-testid="Text"]')
            date_str = date_elem.get_attribute('datetime')
            
            # Handle different date formats
            if '.' in date_str:
                self.date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ") 
            else:
                self.date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ") 

            logger.info(f"Parsed date: {self.date}")
        except (NoSuchElementException, ValueError) as e:
            logger.error(f"Failed to parse date: {str(e)}")
            self.date = None

    def parse_image_link(self) -> None:
        """Parse and set the image link of the news item."""
        try:
            noscript_elements = self.web_element.find_elements(By.TAG_NAME, 'noscript')
            if noscript_elements:
                html = self.web_element.get_attribute('outerHTML')
                match = re.search(r'<noscript><img src="([^"]+)"', html)
                self.image_link = match.group(1) if match else None
            else:
                image_link_elem = self.web_element.find_element(By.CSS_SELECTOR, '[src]')
                self.image_link = image_link_elem.get_attribute('src')
            logger.info(f"Parsed image link: {self.image_link[:20]}......{self.image_link[-20:]}")
        except NoSuchElementException:
            logger.error("Failed to parse image link: Element not found")
            self.image_link = None

    def parse_image_name(self) -> None:
        """Parse and set the image name based on the image link."""
        if self.image_link:
            self.image_name = os.path.basename(self.image_link)
            logger.info(f"Parsed image name: {self.image_name}")
        else:
            logger.warning("No image link available to parse image name")

    def count_search_phrases(self) -> None:
        """Count occurrences of the search phrase in the title."""
        if self.title:
            self.count_phrase = len(re.findall(re.escape(self.search_phrase), self.title, re.IGNORECASE))
            logger.info(f"Count of search phrase in title: {self.count_phrase}")
        else:
            logger.warning("No title available to count search phrases")
            self.count_phrase = 0

    def contains_money(self) -> None:
        """Check if the title contains references to money."""
        if self.title:
            money_pattern = r'\$\d+(?:,\d{3})*(?:\.\d+)?|\d+\s?(?:dollars?|USD)'
            self.contain_money = bool(re.search(money_pattern, self.title, re.IGNORECASE))
            logger.info(f"Contains money: {self.contain_money}")
        else:
            logger.warning("No title available to check for money references")
            self.contain_money = False

    def parse_all(self) -> None:
        """Parse all attributes of the news item."""
        logger.info("Parsing new news item...")
        self.parse_title()
        self.parse_date()
        self.parse_image_link()
        self.parse_image_name()
        self.count_search_phrases()
        self.contains_money()
        logger.info("Finished parsing news item")

class NewsProcessor:
    """
    Processes news items based on search criteria and saves the results.
    """

    def __init__(self, driver, search_phrase: str, section: str = 'all', date_range: int = 1) -> None:
        """
        Initialize the NewsProcessor.

        Args:
            driver: The WebDriver instance.
            search_phrase (str): The phrase to search for in news.
            section (str): The news section to search in.
            date_range (int): The number of months to look back for news.
        """
        self.search_phrase = search_phrase
        self.section = section
        self.date_range = max(1, date_range)  # Ensure date_range is at least 1
        self.driver = driver 
        self.report: List[News] = []
        logger.info(f"Initialized NewsProcessor with search phrase: '{search_phrase}', section: '{section}', date range: {date_range} months")

    def define_section(self) -> str:
        """
        Define the news section to search in.

        Returns:
            str: The validated section name.
        """
        site_categories = ['all', 'world', 'business', 'legal', 'markets', 'breakingviews',
                           'technology', 'sustainability', 'science' ,'sports', 'lifestyle']
        if self.section.lower() in site_categories:
            category_search = self.section.lower()
            logger.info(f"Valid category - Set up as: {category_search}")
        else:
            logger.info('Invalid category - Setting category as All')
            category_search = 'all'
        return category_search

    def define_url(self, offset: int = 0) -> str:
        """
        Define the URL for the news search.

        Args:
            offset (int): The offset for pagination.

        Returns:
            str: The generated URL.
        """
        base_url = 'https://www.reuters.com/site-search/?query='
        encoded_query = urllib.parse.quote(self.search_phrase)
        category = self.define_section()
        url = f"{base_url}{encoded_query}&offset={offset}&section={category}&sort=newest"
        logger.info(f"Generated URL: {url}")
        return url

    def is_within_date_range(self, news_date: datetime) -> bool:
        """
        Check if a news item's date is within the specified date range.

        Args:
            news_date (datetime): The date of the news item.

        Returns:
            bool: True if within range, False otherwise.
        """
        cutoff_date = datetime.now() - timedelta(days=30 * self.date_range)
        result = news_date >= cutoff_date
        logger.info(f"Checking date {news_date}.") 
        logger.info(f"Cutoff date: {cutoff_date}.")
        logger.info(f"Within range: {result}.")
        return result

    def process_news(self, news_elements: List[WebElement]) -> bool:
        """
        Process a list of news elements.

        Args:
            news_elements (List[WebElement]): List of news web elements to process.

        Returns:
            bool: True if should continue processing, False otherwise.
        """
        continue_processing = True
        logger.info(f"Processing {len(news_elements)} news elements")
        for element in news_elements:
            news = News(element, self.search_phrase)
            news.parse_all()
            if self.is_within_date_range(news.date):
                self.report.append(news)
                logger.info(f"Added news item to report. Current report size: {len(self.report)}")
            else:
                continue_processing = False
                logger.info("Found news item outside date range. Stopping processing.")
                break
        return continue_processing

    def iterate_over_pages(self) -> None:
        """Iterate over news pages and process news items."""
        offset = 0
        total_news_processed = 0
        total_news = 0

        while True:
            url = self.define_url(offset)
            logger.info(f"Navigating to URL: {url}")
            self.driver.get(url)

            try:
                logger.info("Checking for 'No search results' message...")
                main_content = WebDriverWait(self.driver, 20).until(
                    EC.visibility_of_element_located((By.ID, 'main-content'))
                )
                if "No search results match" in main_content.text:
                    logger.info("No search results found. Stopping the process.")
                    break

                logger.info("Waiting for search results to load...")
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'search-results__list__2SxSK'))
                )
                logger.info("Search results loaded successfully")

                if offset == 0:
                    logger.info("Extracting total number of results...")
                    count_news_elem = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'search-results__subtitle__3k4lv'))
                    )
                    count_news_elem = count_news_elem.find_element(By.CSS_SELECTOR, '[data-testid="Text"]')
                    count_news_str = re.sub(r'\D', '', count_news_elem.text)
                    total_news = int(float(count_news_str))
                    logger.info(f"Total news found: {total_news}")

                logger.info("Finding news items on the current page...")
                news_list = self.driver.find_element(By.CLASS_NAME, 'search-results__list__2SxSK')
                news_items = news_list.find_elements(By.CLASS_NAME, 'search-results__item__2oqiX')
                logger.info(f"Found {len(news_items)} news items on this page")

                logger.info("Processing news items...")
                continue_processing = self.process_news(news_items)
                total_news_processed += len(news_items)

                logger.info(f"Processed {len(self.report)} news items within the date range")
                logger.info(f"Total news processed so far: {total_news_processed}")

                if not continue_processing:
                    logger.info("Reached news outside of the specified date range. Stopping.")
                    break

                if total_news_processed >= total_news:
                    logger.info(f"Reached or exceeded the total number of news items ({total_news}). Stopping.")
                    break

                offset += 20
                logger.info(f"Moving to next page. New offset: {offset}")

                logger.info("Waiting 2 seconds before next request...")
                time.sleep(2)

            except (NoSuchElementException, TimeoutException) as e:
                logger.error(f"Error processing page with offset {offset}: {str(e)}")
                break

        logger.info(f"Finished iterating over pages. Total news items in report: {len(self.report)}")

    def download_image(self, news, download_path) -> str:
        """
        Download the image for a news item.

        Args:
            news (News): The news item containing the image link.
            download_path (str): The path to save the downloaded image.

        Returns:
            str: The filename of the downloaded image.
        """
        try:
            url = news.image_link
            params = {'behavior': 'allow', 'downloadPath': download_path}
            self.driver.execute_cdp_cmd('Page.setDownloadBehavior', params)

            self.driver.get(url)
            
            download_path = os.path.join(download_path, news.image_name)
            download_path, _ = os.path.splitext(download_path)
            download_path = f"{download_path}.png"
            
            with open((download_path), 'wb') as file:
                file.write(self.driver.find_element(By.TAG_NAME, 'img').screenshot_as_png)
                
                # Wait for download to complete (max 10 seconds)
                for _ in range(10):
                    if list(glob.iglob(download_path)):
                        logger.info(f"Image {news.image_name} saved.")
                        break
                    time.sleep(1)
                else:
                    logger.warning(f"Timeout while waiting for image download: {news.image_name}")

            return os.path.basename(download_path)
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return ""

    def save_to_excel(self) -> None:
        """Save processed news data to an Excel file."""
        try:
            output_folder = "output"
            os.makedirs(output_folder, exist_ok=True)
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            image_folder_full_path = os.path.abspath(output_folder)
            
            data = []
            for news in self.report:
                image_filename = ""
                if news.image_link:
                    image_filename = self.download_image(news, image_folder_full_path)

                data.append({
                    "title": news.title,
                    "date": news.date,
                    "picture_filename": image_filename,
                    "search_phrase_count": news.count_phrase,
                    "contains_money": str(news.contain_money)
                })

            df = pd.DataFrame(data)
            excel_filename = f"NewsReport_{self.search_phrase}_{self.section}_{self.date_range}_{current_date}.xlsx"
            excel_path = os.path.join(output_folder, excel_filename)
            df.to_excel(excel_path, index=False)
            logger.info(f"Excel report saved: {excel_path}")
        except Exception as e:
            logger.error(f"Error saving to Excel: {str(e)}")
        
    def process(self) -> List[News]:
        """
        Process news items based on the search criteria.

        Returns:
            List[News]: A list of processed news items.
        """
        logger.info("Starting news processing...")
        try:
            self.iterate_over_pages()
            logger.info("Saving news to excel file")
            self.save_to_excel()
            logger.info(f"Finished processing. Total news items collected: {len(self.report)}")
            return 'Successful'
        except Exception as e:
            logger.error(f"Error during news processing: {str(e)}")
            return 'Failed'

    def __del__(self):
        """Cleanup method to close the WebDriver when the object is destroyed."""
        if self.driver:
            logger.info("Closing WebDriver...")
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {str(e)}")