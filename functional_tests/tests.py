import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element(By.ID, "id_list_table")
                rows = table.find_elements(By.TAG_NAME, "tr")
                self.assertIn(row_text, [row.text for row in rows])
                return
            except AssertionError as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def check_for_row_in_list_table(self, row_text):
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        self.assertIn(row_text, [row.text for row in rows])

    def test_can_start_a_list_and_retrieve_it_later(self):
        self.browser.get(self.live_server_url)
        self.assertIn("To-Do", self.browser.title)
        header_text = self.browser.find_element(By.TAG_NAME, "h1").text
        self.assertIn("To-Do", header_text)

        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a to-do item")
        inputbox.send_keys("Buy Flowers")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy Flowers")

        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(inputbox.get_attribute("placeholder"), "Enter a to-do item")
        inputbox.send_keys("Give a gift to Lisi")
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table("1: Buy Flowers")
        self.wait_for_row_in_list_table("2: Give a gift to Lisi")

        self.fail("Finish the test!")

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Buy Flowers")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy Flowers")

        user1_list_url = self.browser.current_url
        self.assertRegex(user1_list_url, "/lists/.+")

        self.browser.quit()
        self.browser = webdriver.Chrome()

        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Buy Flowers", page_text)
        self.assertNotIn("Give a gift to Lisi", page_text)

        inputbox = self.browser.find_element(By.ID, "id_new_item")
        inputbox.send_keys("Buy Milk")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy Milk")

        user2_list_url = self.browser.current_url
        self.assertRegex(user2_list_url, "/lists/.+")
        self.assertNotEqual(user2_list_url, user1_list_url)

        page_text = self.browser.find_element(By.TAG_NAME, "body").text
        self.assertNotIn("Buy Flowers", page_text)
        self.assertIn("Buy Milk", page_text)

    def test_layout_and_styling(self):
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertAlmostEqual(
            inputbox.location["x"] + inputbox.size["width"] / 2,
            512,
            delta=10,
        )

