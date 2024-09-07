import logging

from robocorp import workitems
from robocorp.tasks import task
from RPA.core.webdriver import download, start

from custom_selenium import CustomSelenium
from news_processor import NewsProcessor

# Configure the Logger
logger = logging.getLogger(__name__)
FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)


@task
def news_extraction_process():
    logger.info("Starting automation...")

    # define driver connection
    logger.info("Defining web driver.")
    selenium = CustomSelenium()
    selenium.set_webdriver()

    # Get work items
    logger.info("Getting work items to process.")
    for item in workitems.inputs:
        try:
            search_phrase = item.payload["search_phrase"]
            section = item.payload["section"]
            date_range = int(float(item.payload["date_range"]))
            logger.info(
                f"Received work item - Search Phrase: {search_phrase},Section: {section},Date range: {date_range}"
            )

            processor = NewsProcessor(
                selenium.driver, search_phrase, section, date_range
            )
            status = processor.process()
            if "Failed" in status:
                raise Exception("Exception during news extraction.")

            item.done()

        except KeyError as err:
            item.fail("APPLICATION", code="MISSING_FIELD", message=str(err))
            logger.exception(f"MISSING_FIELD - {str(err)}.")
        except Exception as exc:
            item.fail("APPLICATION", code="SYSTEM_EXCEPTION", message=str(exc))
            logger.error(f"SYSTEM EXCEPTION - {str(exc)}.")
