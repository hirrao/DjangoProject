import unittest

from selenium import webdriver


class NewVisitorTest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_start(self):
        self.browser.get("http://127.0.0.1:8000/")
        self.assertIn("TO-DO", self.browser.title)
        self.fail("Finish the test!")

if __name__ == '__main__':
    unittest.main()
