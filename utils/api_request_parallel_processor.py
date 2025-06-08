import requests

import concurrent.futures

class APIRequestParallelProcessor:
    def __init__(self, urls, max_workers=5):
        """
        Initialize the processor with a list of URLs and maximum number of workers.
        :param urls: List of URLs to process.
        :param max_workers: Maximum number of threads to use for parallel processing.
        """
        self.urls = urls
        self.max_workers = max_workers

    def fetch_url(self, url):
        """
        Fetch the content of a URL.
        :param url: URL to fetch.
        :return: Response content or error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error fetching {url}: {e}"

    def process_requests(self):
        """
        Process all URLs in parallel.
        :return: Dictionary with URL as key and response content or error message as value.
        """
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_url, url): url for url in self.urls}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = f"Error processing {url}: {e}"
        return results

# Example usage:
if __name__ == "__main__":
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/posts/3",
    ]
    processor = APIRequestParallelProcessor(urls, max_workers=3)
    results = processor.process_requests()
    for url, content in results.items():
        print(f"URL: {url}\nContent: {content}\n")