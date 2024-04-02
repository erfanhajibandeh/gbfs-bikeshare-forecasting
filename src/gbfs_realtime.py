import requests
import time
import json

class GBFSRealTimeData:
    """
    A class to download the real-time General Bikeshare Feed Specification (GBFS) data for Lyft BayWheels.
    
    Attributes:
        base_url (str): The base URL for the GBFS feeds.
        feeds (dict): A dictionary mapping feed names to their respective endpoint extensions.
    """
    def __init__(self, base_url, feeds):
        """
        Initializes the GBFSRealTimeData object with base URL and feeds.
        
        Parameters:
            base_url (str): The base URL for the GBFS data.
            feeds (dict): A dictionary of feed names and their URL extensions.
        """
        self.base_url = base_url
        self.feeds = feeds
    
    def select_feeds(self):
        """
        Allows the user to select which feeds to download via the command line.
        
        Users can select feeds by entering their numbers, ranges with ':', or type 'all' for all feeds.
        
        Returns:
            list: A list of selected feed names to be downloaded.
        """
        print("Available feeds for download:")
        for idx, feed in enumerate(self.feeds.keys(), start=1):
            print(f"{idx}. {feed}")
        
        choice = input("Select the numbers of the feeds to download separated by commas, ranges with ':', or type 'all' to download everything: ").strip()
        
        if choice.lower() == 'all':
            selected_feeds = list(self.feeds.keys())
        else:
            selected_indices = self._parse_user_choice(choice, len(self.feeds))
            selected_feeds = [list(self.feeds.keys())[i - 1] for i in selected_indices]
        
        return selected_feeds
    
    def _parse_user_choice(self, choice, num_feeds):
        """
        Parses the user's selection input into indices of the feeds to download.
        
        Parameters:
            choice (str): The user's input for selected feeds.
            num_feeds (int): The total number of available feeds.
        
        Returns:
            list: A list of indices for the selected feeds.
        """
        selected_indices = []
        parts = choice.split(',')

        for part in parts:
            if ':' in part:
                start, end = map(int, part.split(':'))
                selected_indices.extend(range(start, end + 1))
            elif part.isdigit():
                selected_indices.append(int(part))
        
        return sorted(set(index for index in selected_indices if 0 < index <= num_feeds))
    
    def _dump_collected_data(self, feed_data):
        """
        Dumps the collected data for each feed into separate JSON files.
        
        Parameters:
            feed_data (dict): A dictionary containing the feed names and their collected data lists.
        """
        for feed_name, data in feed_data.items():
            file_name = f"{feed_name}.json"  
            with open(file_name, 'w') as file:
                json.dump(data, file)
            print(f"Dumped data for {feed_name} into {file_name}")

    def download_and_process_data(self, selected_feeds, duration, interval):
        """
        Downloads and processes the data for the selected feeds for a specified duration at given intervals.
        
        Parameters:
            selected_feeds (list): A list of feed names to download.
            duration (int): The duration in seconds for which to run the download process.
            interval (int): The interval in seconds between data downloads.
            
        Returns:
            dict: A dictionary with feed names as keys and lists of collected data as values.
        """
        end_time = time.time() + duration
        feed_data = {feed: [] for feed in selected_feeds}
        
        while time.time() < end_time:
            download_time = time.time()
            for feed in selected_feeds:
                try:
                    url = self.base_url + self.feeds[feed]
                    response = requests.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        feed_data[feed].append(data)
                    else:
                        print(f"Failed to download {feed}. Status code: {response.status_code}")
                except Exception as e:
                    print(f"An error occurred while downloading {feed}: {e}")
                    
            time.sleep(interval)
        
        self._dump_collected_data(feed_data)  
        print('Selected data were successfully exported to the currect working directory')
        return feed_data

if __name__ == "__main__":

    base_url = "https://gbfs.lyft.com/gbfs/2.3/bay/"
    feeds = {
        "gbfs": "gbfs.json",
        "system_information": "en/system_information.json",
        "station_information": "en/station_information.json",
        "station_status": "en/station_status.json",
        "free_bike_status": "en/free_bike_status.json",
        "system_hours": "en/system_hours.json",
        "system_calendar": "en/system_calendar.json",
        "system_regions": "en/system_regions.json",
        "system_pricing_plans": "en/system_pricing_plans.json",
        "system_alerts": "en/system_alerts.json",
        "gbfs_versions": "en/gbfs_versions.json",
        "vehicle_types": "en/vehicle_types.json",
    }
    print("Bay Wheels Real Time Data Download Script")
    print("=========================")
    duration = int(input("Enter the duration (in seconds) for the script to run: "))
    interval = int(input("Enter the interval (in seconds) between each data download: "))
    
    downloader = GBFSRealTimeData(base_url, feeds)
    selected_feeds = downloader.select_feeds()
    collected_data = downloader.download_and_process_data(selected_feeds, duration, interval)