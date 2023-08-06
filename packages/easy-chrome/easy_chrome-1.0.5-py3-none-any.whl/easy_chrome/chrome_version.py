import os
import subprocess
import winreg
import logging
import requests
from zipfile import ZipFile
from io import BytesIO
import xml.etree.ElementTree as elemTree


logger = logging.getLogger(__name__)
logging.basicConfig(level="INFO")

LOCAL_FOLDER = os.path.join(os.path.expanduser("~"), ".chrome_driver")
os.makedirs(LOCAL_FOLDER, exist_ok=True)
TRIED = False


def get_chrome_installed(hive, flag):
    """get installed chrome version from winreg"""
    try:
        a_reg = winreg.ConnectRegistry(None, hive)
        a_key = winreg.OpenKey(a_reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | flag)
        a_sub = winreg.OpenKey(a_key, "Google Chrome")
        return winreg.QueryValueEx(a_sub, "DisplayVersion")[0]
    except:
        pass


def get_web_chrome_link(version):
    """get selenium chromedriver version by major version got from local chrome"""
    logger.info("Try to get target chrome driver in web")

    res = requests.get("https://chromedriver.storage.googleapis.com")
    root = elemTree.fromstring(res.content)
    for k in root.iter('{http://doc.s3.amazonaws.com/2006-03-01}Key'):
        if k.text.find(version + '.') == 0:
            ver = k.text.split('/')[0]
            logger.info(f"found web_version: {ver}")
            return ver
    logger.warning(f"not found matched version of chrome: {version}")


def download_web_chrome(version, chrome_driver):
    """download web chromedriver"""
    web_version = get_web_chrome_link(version)

    logger.info(f"Try to download from web: {web_version}")
    link = f"https://chromedriver.storage.googleapis.com/{web_version}/chromedriver_win32.zip"
    res = requests.get(link)
    with ZipFile(BytesIO(res.content)) as zip_file:
        for info in zip_file.infolist():
            if info.filename == "chromedriver.exe":
                info.filename = chrome_driver
                zip_file.extract(info, LOCAL_FOLDER)
                return


def get_chrome_version():
    """get chromedriver version, download if needed"""
    chrome_driver = 'chromedriver.exe'
    version = ""
    try:
        if os.path.exists("C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"):
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" '
                r'get Version /value', shell=True)
        else:
            output = subprocess.check_output(
                r'wmic datafile where name="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
                r'get Version /value', shell=True)

        version = output.decode('utf-8').strip().split("=")[1].split(".")[0]

        chrome_driver = f'chromedriver_{version}.exe'
    except:
        for hive, flag in ((winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
                           (winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
                           (winreg.HKEY_CURRENT_USER, 0)):
            cr_ver = get_chrome_installed(hive, flag)
            if cr_ver is not None:
                version = str(cr_ver).split(".")[0]
                chrome_driver = f'chromedriver_{version}.exe'
                break

    global TRIED
    if version != "" and not TRIED and not os.path.exists(os.path.join(LOCAL_FOLDER, chrome_driver)):
        try:
            download_web_chrome(version, chrome_driver)
        finally:
            TRIED = True

    logger.info(f"found version: {chrome_driver}")

    return chrome_driver
