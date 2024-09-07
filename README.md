# News Scraper Automation
Developed by Alexandre Dutra
## Overview

This project is an automated news scraper built as part of the Thoughtful RPA Coding Challenge. It extracts data from [Reuters](https://www.reuters.com/) based on specific search criteria and saves the results in an Excel file along with downloaded images.

## Features

- Searches for news articles based on a given phrase
- Filters news by category/section
- Collects news from a specified time range
- Extracts title and date of news articles
- Downloads associated images
- Counts occurrences of the search phrase in the title and description
- Detects mentions of money in the title or description
- Saves all collected data in an Excel file

## Technologies Used

- Python 3.8+
- Custom Selenium WebDriver
- pandas for data manipulation and Excel file creation (included in the Conda environment)

## Project Structure

- `tasks.py`: Main entry point for the RPA process
- `news_processor.py`: Core logic for news processing and data extraction
- `custom_selenium.py`: Custom wrapper around Selenium

## Setup and Installation

1. Clone this repository inside a robocorp project
2. Create the work items in requested structure
3. The project uses a Conda environment configuration, which includes all necessary dependencies including pandas. No additional installation of packages is required.


## Usage

The script is designed to be run as a Robocorp Control Room process. It expects the following parameters to be provided via a Robocloud work item:

| Key            | Description                                                                                                                                                    |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `search_phrase`| The phrase to search for in news articles                                                                                                                       |
| `section`      | The news category/section to filter. Valid options: `all`, `world`, `business`, `legal`, `markets`, `breakingviews`, `technology`, `sustainability`, `science`, `sports`, `lifestyle`. If not specified or invalid, defaults to `all`. |
| `date_range`   | Number of months to look back for news (0 or 1 for current month only)                                                                                          |

## Output

The script generates two types of output:

1. An Excel file named `NewsReport_{search_phrase}_{section}_{date_range}_{timestamp}.xlsx` containing the extracted data
2. Image files saved directly in the root directory, with filenames stored on the excel report.

## Logging

The script uses Python's built-in logging module to provide detailed logs of its operation. Log messages are printed to the console and can be accessed on `log.html`.

## Error Handling

The script includes error handling to manage common issues such as network errors, missing elements, and timeouts. It will attempt to continue processing even if individual news items fail to load or parse correctly.
