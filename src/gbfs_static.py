import os
import pandas as pd
import requests
import zipfile
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GBFSStaticData:
    """
    A class to scrape, download, and process static GBFS data from zip files available for Lyft BayWheels.

    Attributes:
        url (str): The URL from which to scrape zip file links.
        dataframes (list): A list to store processed data from the downloaded CSV files.
    """

    def __init__(self, url: str):
        """
        Initializes the GBFSStaticData object with a URL and an empty list for dataframes.

        Parameters:
            url (str): The URL from which to scrape zip file links.
        """
        self.url = url
        self.dataframes = []

    def get_gbfs_links(self):
        """
        Scrapes the specified URL for links to zip files containing GBFS data.

        Uses Selenium and Chrome WebDriver to navigate and scrape the webpage.

        Returns:
            list: A list of URLs to the zip files found on the page.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        links = [] 

        try:
            driver.get(self.url)
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, 'a')))
            a_tags = driver.find_elements(By.TAG_NAME, 'a')
            links = [tag.get_attribute('href') for tag in a_tags if tag.get_attribute('href') and tag.get_attribute('href').endswith('.zip')]

        except Exception as e:
            print(f"Error: {e}")

        finally:
            driver.quit()
            return links

    def download_and_process_data(self, urls):
        """
        Downloads and processes data from the specified URLs of zip files.

        Each zip file is downloaded to a temporary directory, extracted, and then each contained CSV file is processed.

        Parameters:
            urls (list): A list of URLs to download and process.
        """
        for url in urls:
            print(f"Processing: {url.split('/')[-1].split('-')[0:2]}")
            # Create a temporary directory for ZIP files
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = self._download_zip(url, temp_dir)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.csv'):
                        csv_path = os.path.join(temp_dir, filename)
                        self._append_to_df(csv_path)


    def _download_zip(self, url, temp_dir):
        """
        Downloads a zip file from the specified URL to a temporary directory.

        Parameters:
            url (str): The URL to download the zip file from.
            temp_dir (str): The path to the temporary directory to store the downloaded zip file.

        Returns:
            str: The path to the downloaded zip file.
        """
        local_filename = os.path.join(temp_dir, url.split('/')[-1])
        with requests.get(url, stream=True) as r:
            with open(local_filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return local_filename

    def _append_to_df(self, csv_path):
        """
        Appends data from a CSV file to the appropriate dataframe in self.dataframes.

        Parameters:
            csv_path (str): The path to the CSV file to process.
        """
        new_df = pd.read_csv(csv_path)
        new_columns = new_df.columns.tolist()  # Get column names as a list

        for i, df in enumerate(self.dataframes):
            # Compare column names
            if set(df.columns.tolist()) == set(new_columns):
                self.dataframes[i] = pd.concat([df, new_df], ignore_index=True)
                return

        self.dataframes.append(new_df)

    def user_select_urls(self):
        """
        Allows the user to select specific zip file URLs for download and processing via the command line.
        """
        urls = self.get_gbfs_links()

        if urls:
            print("Available .zip files for download:")
            for idx, url in enumerate(urls, start=1):
                print(f"{idx}. {url.split('/')[-1].split('-')[0:2]}")

            choice = input("Select the numbers of the files to download separated by commas, ranges with ':', or type 'all' to download everything: ").strip()
            if choice.lower() == 'all':
                selected_urls = urls
            else:
                selected_indices = self._parse_user_choice(choice, len(urls))
                selected_urls = [urls[i - 1] for i in selected_indices]

            self.download_and_process_data(selected_urls)
        else:
            print("No .zip files found.")

    def _parse_user_choice(self, choice, num_urls):
        selected_indices = []
        parts = choice.split(',')

        for part in parts:
            if ':' in part:
                start, end = map(int, part.split(':'))
                selected_indices.extend(range(start, end + 1))
            elif part.isdigit():
                selected_indices.append(int(part))

        return sorted(set(index for index in selected_indices if 0 < index <= num_urls))


if __name__ == "__main__":
    print("Bay Wheels Static Data Download Script")
    print("=========================")
    downloader = GBFSStaticData(url='https://s3.amazonaws.com/baywheels-data/index.html')
    downloader.user_select_urls()
    

    for idx, df in enumerate(downloader.dataframes, start=1):
        df.to_csv(f"gbfs_dataframe_{idx}.csv", index=False)
    print('Selected data were successfully exported to the currect working directory')

