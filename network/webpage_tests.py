import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Finds the Uniform Resourse Identifier of a file
def file_uri(path):
    return f"http://127.0.0.1:8000{path}"

# Sets up web driver using Google chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


class WebpageTests(unittest.TestCase):

    def test_title(self):
        """Make sure title is correct"""
        driver.get(file_uri("/"))
        self.assertEqual(driver.title, "All Posts")

if __name__ == "__main__":
    unittest.main()