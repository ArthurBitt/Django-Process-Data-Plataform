from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Tuple
from decouple import config as decouple_config

class CustomDriver:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # options.add_argument("--headless")

        if not decouple_config("EXECUTE_WITH_REMOTE_WEB_DRIVER", cast=bool):
            self.driver = webdriver.Chrome(
                options=options,
                service=ChromeService(ChromeDriverManager().install()),
            )
        else:
            self.driver = webdriver.Remote(
                command_executor=decouple_config("REMOTE_WEBDRIVER"),
                options=options,
            )
            self.driver.maximize_window()

    def get_url(self, url):
        self.driver.get(url)

    def get_element_by_id(self, element_id, wait=10) -> WebElement:
        return WebDriverWait(self.driver, wait).until(
            ec.presence_of_element_located((By.ID, element_id))
        )

    def get_elements_by_id(self, element_id, wait=10) -> List[WebElement]:
        return WebDriverWait(self.driver, wait).until(
            ec.presence_of_all_elements_located((By.ID, element_id))
        )

    def get_element_by_xpath(self, xpath, wait=10) -> WebElement:
        return WebDriverWait(self.driver, wait).until(
            ec.presence_of_element_located((By.XPATH, xpath))
        )

    def get_elements_by_xpath(self, xpath, wait=10) -> List[WebElement]:
        return WebDriverWait(self.driver, wait).until(
            ec.presence_of_all_elements_located((By.XPATH, xpath))
        )

    def switch_to_default_content(self):
        self.driver.switch_to.default_content()

    def switch_to_frame_by_id(self, frame_id, wait=10):
        WebDriverWait(self.driver, wait).until(
            ec.frame_to_be_available_and_switch_to_it((By.ID, frame_id))
        )

    def wait_for_element(self, tag_name, wait=60):
        return WebDriverWait(self.driver, wait).until(
            ec.presence_of_element_located((By.XPATH, tag_name))
        )
    def quit(self):
        self.driver.quit()