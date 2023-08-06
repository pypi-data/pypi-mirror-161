import os
import re
import subprocess
import zipfile

import requests

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import SessionNotCreatedException, TimeoutException

from .enums import GoogleChrome
from .exceptions import BrowserNotInstalledException

class ChromeDriver():
    """
    ChromeDriver provides a selenium webdriver for the current installation of
    Google Chrome as well as a set of generic functions for common actions such
    as locating elements and user input.

    NB: ChromeDriver requires a working internet connection to download the latest
    release of the chromedriver applicable to the current installation of Google
    Chrome.
    """
    def __init__(self):
        self.webdriver = self._setup_chromedriver()

    def element_is_clickable(self, by: By, criteria: str, **kwargs):
        """
        Checks that an element is clikcable on the DOM of a page and returns the
        WebElement if it is located within the timeout period.

        Args:
         - by: By object used to locate the element. E.g. By.XPATH
         - criteria: the search criteria to use. E.g. '//input[@id="login-button"]'
         - timeout (optional): the timeout period. E.g. 60 seconds
         - name(optional): the name of the element. E.g. "login button"

        Raises a TimeoutException if the specified element cannot be located within
        the specified timeout period.
        """
        name = kwargs["name"] if "name" in kwargs.keys() else criteria
        timeout = kwargs["timeout"] if "timeout" in kwargs.keys() else 60 

        try:
            element = WebDriverWait(self.webdriver, timeout=timeout).until(
                expected_conditions.presence_of_element_located((by, criteria)))
        except TimeoutException:
            raise TimeoutException(f"{name} could not be located in {timeout} seconds.")
        else:
            return element

    def element_is_present(self, by: By, criteria: str, **kwargs):
        """
        Checks that an element is present on the DOM of a page and returns the
        WebElement if it is located within the timeout period.

        Args:
         - by: By object used to locate the element. E.g. By.XPATH
         - criteria: the search criteria to use. E.g. '//input[@id="login-form"]'
         - timeout (optional): the timeout period. E.g. 60 seconds
         - name(optional): the name of the element. E.g. "login form"

        Raises a TimeoutException if the specified element cannot be located within
        the specified timeout period.
        """
        name = kwargs["name"] if "name" in kwargs.keys() else criteria
        timeout = kwargs["timeout"] if "timeout" in kwargs.keys() else 60 

        try:
            element = WebDriverWait(self.webdriver, timeout=timeout).until(
                expected_conditions.presence_of_element_located((by, criteria)))
        except TimeoutException:
            raise TimeoutException(f"{name} could not be located in {timeout} seconds.")
        else:
            return element

    def get_field_value(self, field: str, level=1):
        """
        Returns the value of the provided field.

        Args:
         - field: the field whose value should be retrieved
        """
        element = self.element_is_present(By.XPATH, f'//*[text()="{field}"]')
        relative_xpath = ".."if level == 1 else ("../" * level)[:-1]
        parent_element = element.find_element(By.XPATH, relative_xpath)

        if bool(parent_element.find_elements(By.TAG_NAME, "select")):
            return Select(parent_element.find_element(
                By.TAG_NAME, "select")).first_selected_option.text

        if bool(parent_element.find_elements(By.TAG_NAME, "input")):
            return parent_element.find_element(
                By.TAG_NAME, "input").get_attribute("value")

        if bool(parent_element.find_elements(By.TAG_NAME, "div")):
            return parent_element.find_element(By.TAG_NAME, "div").text

    def press(self, key: Keys, number_of_times=1):
        """
        Presses the provided key "n" number of times.

        Args:
         - key: Keys objects to press. E.g. Keys.ARROW_UP
         - number_of_times (optional): the number of times to press the key (default = 1)
        """
        action_chains = ActionChains(self.webdriver)
        for _ in range(number_of_times):
            action_chains.key_down(key).perform()

    def set_field_value(self, field: str, value: str, level=1, select_by="index"):
        """
        Sets the value of the provided field.

        Args:
         - field: the field to set. E.g. "Username:"
         - value: the value to set the field to. E.g. "Foo"
        """
        element = self.element_is_present(By.XPATH, f'//*[text()="{field}"]')
        relative_xpath = ".." if level == 1 else ("../" * level)[:-1]
        parent_element = element.find_element(By.XPATH, relative_xpath)
        value = str(value)

        if bool(parent_element.find_elements(By.TAG_NAME, "select")):
            if select_by == "index":
                return Select(parent_element.find_element(
                    By.TAG_NAME, "select")).select_by_index(value)
            if select_by == "text":
                return Select(parent_element.find_element(
                    By.TAG_NAME, "select")).select_by_visible_text(value)
            if select_by == "value":
                return Select(parent_element.find_element(
                    By.TAG_NAME, "select")).select_by_value(value)

        if bool(parent_element.find_elements(By.TAG_NAME, "input")):
            try:
                element = parent_element.find_element(By.TAG_NAME, "input")
                element.clear()
                element.send_keys(value)
            except:
                element = parent_element.find_element(By.TAG_NAME, "input").click()

    def _download_chromedriver(self):
        if not os.path.exists(self._chromedriver_exe):
            version_number = self._get_version_number()
            latest_release = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{version_number}")
            latest_release = latest_release.content.decode("utf-8")
            with requests.get(f"https://chromedriver.storage.googleapis.com/{latest_release}/chromedriver_win32.zip", stream=True) as download:
                download.raise_for_status()
                with open(os.path.join(self._chromedriver_zip), "wb") as chromedriver_zip:
                    for chunk in download.iter_content(chunk_size=1024):
                        chromedriver_zip.write(chunk)
                self._unzip_chromedriver()

    def _get_version_number(self):
        for bit_version in GoogleChrome:
            version = subprocess.check_output(
                bit_version.value,
                shell=True
            ).decode("UTF-8")
            if bool(version):
                try:
                    version = re.search("([0-9]+.){3}[0-9]+", version)[0].split(".")
                    return ".".join(version[:-1])
                except TypeError:
                    continue
        else:
            raise BrowserNotInstalledException("""Google Chrome is not installed in the default \"C:\\Program Files\" directories.""")

    def _setup_chromedriver(self):
        self._chromedriver_exe = "chromedriver.exe"
        self._chromedriver_zip = os.path.join(os.getcwd(), "chromedriver_win32.zip")
        self._download_chromedriver()

        try:
            options = Options()
            options.add_experimental_option("excludeSwitches",
                ["enable-automation", "enable-logging"])
            webdriver = Chrome(
                options=options,
                service=Service(self._chromedriver_exe)
            )
        except SessionNotCreatedException:
            os.remove(self._chromedriver_exe)
            self._setup_chromedriver()
        else:
            return webdriver

    def _unzip_chromedriver(self):
        with zipfile.ZipFile(self._chromedriver_zip, "r") as zip_file:
            zip_file.extractall(os.getcwd())
        os.remove(self._chromedriver_zip)