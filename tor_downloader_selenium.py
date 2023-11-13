from datetime import datetime
import json
import os
import pyautogui
import sys
import re
import pyperclip
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from urllib.parse import urlparse, unquote


def process_file(file_path):
    base_download_path = create_download_path()
    urls = extract_urls(file_path)
    tor_browser = get_tor_browser()
    url_details = []

    for url in urls:
        url_data = process_url(url, base_download_path, tor_browser)
        url_details.append(url_data)

    json_path = os.path.join(base_download_path, "url_details.json")
    with open(json_path, "w") as json_file:
        json.dump(url_details, json_file, indent=4)


def get_tor_browser():
    # Path to Tor Browser
    tor_browser_path = "/home/benfred/.local/share/torbrowser"
    if not os.path.exists(tor_browser_path):
        raise ValueError("Invalid Tor Browser path")
    # Path to Tor Browser executable & profile
    tor_binary_path = os.path.join(
        tor_browser_path, "tbb/x86_64/tor-browser/Browser/firefox"
    )
    tor_profile_path = os.path.join(
        tor_browser_path,
        "tbb/x86_64/tor-browser/Browser/TorBrowser/Data/Browser/profile.default",
    )

    # Setup Selenium WebDriver to use Tor Browser
    options = Options()
    options.binary_location = tor_binary_path
    options.profile = tor_profile_path

    # Note: Tor Browser already configured to use Tor network, no need to set proxy
    tor_browser = webdriver.Firefox(options=options)

    return tor_browser


def create_download_path():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    download_path = f"downloads_{timestamp}"
    os.makedirs(download_path)
    return download_path


def extract_urls(file_path):
    """Extract all HTTP(S) URLs from a file"""
    with open(file_path, "r") as file:
        text = file.read()
    return re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )


def process_url(url, base_download_path, driver: webdriver.Firefox):
    try:
        download_path = create_subfolders(base_download_path, url)
        if download_path:
            url_data = download_media(url, download_path, driver)
        else:
            url_data = {"url": url, "status": "No file was downloaded."}
    except Exception as e:
        url_data = {"url": url, "status": f"Failed! [{e}]"}

    return url_data


def create_subfolders(base_folder, url: str):
    """Create subfolders based on URL path, excluding the filename"""
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.split("/")
    file_name = path_parts[-1]
    # We are only interested in files (last part of path has a dot extension)
    if not "." in file_name:
        return None

    folder_structure = os.path.join(base_folder, parsed_url.netloc, *path_parts[:-1])
    folder_structure = unquote(folder_structure)  # Decode URL-encoded paths

    if not os.path.exists(folder_structure):
        os.makedirs(folder_structure)
    file_path = os.path.join(folder_structure, file_name)
    return os.path.abspath(file_path)


def download_media(url, file_path, driver: webdriver.Firefox):
    driver.get(url)
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "s")
    time.sleep(0.1)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyperclip.copy(file_path)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.1)
    pyautogui.press("enter")
    time.sleep(0.1)

    url_data = {"url": url, "status": "Successfully downloaded."}
    return url_data


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        process_file(file_path)
    else:
        print("No file path provided as a command-line argument.")


if __name__ == "__main__":
    main()
