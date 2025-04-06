from concurrent.futures import ThreadPoolExecutor, as_completed


class ThreadedScraper:
    def __init__(self, scrape_func, max_workers=None):
        """
        Initialize the scraper with a scraping function and a maximum number of worker threads.

        :param scrape_func: The function to scrape a post given its ID.
        :param max_workers: Maximum number of threads to use concurrently.
        """
        self.scrape_func = scrape_func
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures = []

    def process_post(self, post_id):
        """
        Submit the scraping task for a given post ID to the thread pool.

        :param post_id: The ID of the post to scrape.
        :return: A Future object representing the result of the task.
        """
        future = self.executor.submit(self.scrape_func, post_id)
        self.futures.append(future)
        return future

    def wait_all(self):
        """
        Wait for all submitted tasks to complete and return their results.

        :return: A list of results from all scraping tasks in the order they were submitted.
        """
        results = []
        for future in self.futures:
            results.append(future.result())
        self.futures.clear()  # Clear the futures list after retrieving results
        return results

    def shutdown(self, wait=True):
        """
        Shutdown the executor and free resources.

        :param wait: If True, wait for all pending tasks to complete before shutting down.
        """
        self.executor.shutdown(wait=wait)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
        return False
