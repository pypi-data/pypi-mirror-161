from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import WebDriverException
import selenium.webdriver.support.expected_conditions as EC
import os
import logging
import functools
from contextlib import suppress
from typing import List
from time import sleep
from easy_chrome.chrome_version import get_chrome_version, LOCAL_FOLDER
from selenium.webdriver.common.keys import Keys

logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

CHROME = webdriver.Chrome
CHROME_VERSION = get_chrome_version()


def selenium_error(func):
    @functools.wraps(func)
    def xpath_wrapper(self, xpath, *args, **kwargs):
        try:
            value = func(self, xpath, *args, **kwargs)
        except WebDriverException as e:
            e.msg = getattr(e, "msg", "") + f"{func.__name__}, xpath: {xpath}"  # Update xpath to message
            raise
        return value

    return xpath_wrapper


class Element:
    """
    Custom function for selenium chrome element
    """
    def __init__(self, element):
        self.ele = element

    def __getattr__(self, attr: str):
        return getattr(self.ele, attr)

    def get_text(self):
        """get selement text"""
        return self.ele.text

    def clear_and_type(self, content: str):
        """clear input and type content"""
        self.clear()
        sleep(0.5)
        self.send_keys(content)

    def select_value(self, value):
        """select element by value"""
        Select(self.ele).select_by_value(value)

    def select_visible_text(self, text):
        """select element by text"""
        Select(self.ele).select_by_visible_text(text)

    def select_index(self, index):
        """select element by index"""
        Select(self.ele).select_by_index(index)

    def find_xpath_element(self, xpath):
        """find element by xpath from a element"""
        return Element(self.ele.find_element(By.XPATH, xpath))

    def find_xpath_elements(self, xpath):
        """find elements by xpath from a element"""
        return Element(self.ele.find_elements(By.XPATH, xpath))

    def __call__(self):
        return self.ele


class Driver:
    _default_wait_time = 30

    def __init__(self, driver_: webdriver.Chrome = None):
        self.driver_: webdriver.Chrome = driver_

    def __getattr__(self, attr):
        return getattr(self.driver_, attr)

    def __del__(self):
        if self.driver_ is not None:
            with suppress(Exception):
                self.driver_.quit()

    def set_chrome(self, keep_open: str = "Close", download_dir: str = None, load_cookies: bool = False, proxy=""):
        """
        :param keep_open: str: chosen from 'Close', 'Keep_Open', 'headless'
        :param download_dir: download directory
        :param load_cookies: load from user directory or open incognito mode
        :param proxy: proxy_server:port
        :return:
        """
        chrome_options = webdriver.ChromeOptions()

        if download_dir is not None:
            prefs = {"download.default_directory": os.path.abspath(download_dir)}
            chrome_options.add_experimental_option("prefs", prefs)

        if "Keep_Open" in keep_open:
            chrome_options.add_experimental_option("detach", True)
        else:
            chrome_options.add_experimental_option("detach", False)
            if "headless" in keep_open:
                chrome_options.headless = True

        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')

        if ":" in str(proxy):
            chrome_options.add_argument('--proxy-server=http://{}'.format(proxy))

        chrome_options.add_experimental_option("excludeSwitches",
                                               ["ignore-certificate-errors",
                                                "safebrowsing-disable-download-protection",
                                                "safebrowsing-disable-auto-update",
                                                "disable-client-side-phishing-detection",
                                                'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        if load_cookies:
            dirs = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Google\\Chrome\\User Data"
            chrome_options.add_argument("--user-data-dir=" + dirs)

        else:
            chrome_options.add_argument("--incognito")

        chrome_options.add_argument('--log-level=3')
        chrome_options.add_argument('--disable-logging')

        self.driver_ = webdriver.Chrome(executable_path=os.path.join(LOCAL_FOLDER, CHROME_VERSION),
                                        options=chrome_options)

    def wait(self, wait_time=_default_wait_time):
        return WebDriverWait(self.driver_, wait_time)

    @selenium_error
    def wait_presence(self, xpath: str, wait_time: int = _default_wait_time) -> Element:
        """wait element to presence"""
        return Element(self.wait(wait_time).until(EC.presence_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_visible(self, xpath: str, wait_time: int = _default_wait_time) -> Element:
        """wait element to be visible"""
        return Element(self.wait(wait_time).until(EC.visibility_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_invisible(self, xpath: str, wait_time: int = _default_wait_time) -> Element:
        """wait element to be invisible"""
        return Element(self.wait(wait_time).until(EC.invisibility_of_element_located((By.XPATH, xpath))))

    @selenium_error
    def wait_clickable(self, xpath: str, wait_time: int = _default_wait_time) -> Element:
        """wait element to be clickable"""
        return Element(self.wait(wait_time).until(EC.element_to_be_clickable((By.XPATH, xpath))))

    def get_element(self, xpath) -> Element:
        """get element by Xpath"""
        return Element(self.driver_.find_element(by=By.XPATH, value=xpath))

    def get_elements(self, xpath) -> List[Element]:
        """get list of elements by Xpath"""
        return [Element(item) for item in self.driver_.find_elements(by=By.XPATH, value=xpath)]

    def set_session_storage(self, key, value):
        """
        :param key: session storage key
        :param value: session storage value
        """
        self.driver_.execute_script("return window.sessionStorage.setItem(arguments[0], arguments[1]);", key, value)

    def set_local_storage(self, key, value):
        """
        :param key: local storage key
        :param value: local storage value
        """
        self.driver_.execute_script("return window.localStorage.setItem(arguments[0], arguments[1]);", key, value)

    def remove_local_storage(self, key):
        """
        :param key: local storage key to remove
        """
        self.set_local_storage(key, "")
        self.driver_.execute_script("return window.localStorage.removeItem(arguments[0]);", key)

    def get_session_storage(self, key):
        """
        :param key: session storage key to get
        """
        return self.driver_.execute_script("return window.sessionStorage.getItem(arguments[0]);", key)

    def get_local_storage(self, key):
        """
        :param key: local storage key to get
        """
        return self.driver_.execute_script("return window.localStorage.getItem(arguments[0]);", key)

    def get_local_storage_keys(self):
        """
        :return: get all current driver local storage keys
        """
        return self.driver_.execute_script("return Object.keys(window.localStorage);")

    def get_cookies_string(self):
        """
        :return: current driver cookies in key=value; key=value format
        """
        cookies = self.driver_.get_cookies()
        cookies_string = '; '.join(['{}={}'.format(cookie['name'], cookie['value']) for cookie in cookies])
        return cookies_string

    def get_user_agent(self):
        """
        :return: get current driver user agent
        """
        return self.driver_.execute_script("return navigator.userAgent;")

    def expand_shadow_element(self, element):
        """
        :param element: element which has shadow root
        :return: tree under shadow root
        """
        return self.driver.execute_script('return arguments[0].shadowRoot', element)

    @property
    def user_agent(self):
        """
        :return: user_agent as property
        """
        return self.driver_.execute_script("return navigator.userAgent;")
