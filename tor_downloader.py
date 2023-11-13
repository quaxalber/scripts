from datetime import datetime
import json
import os
import re
import sys
import requests
from requests.exceptions import Timeout
import socket
import socks
import time
from urllib.parse import urlparse, unquote


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "TE": "trailers",
}
"""Custom headers mimicking Tor Browser on Linux"""


def process_file(file_path):
    setup_tor_proxy()
    base_download_path = create_download_path()
    urls = extract_urls(file_path)
    url_details = []

    for url in urls:
        url_data = process_url(url, base_download_path)
        url_details.append(url_data)

    json_path = os.path.join(base_download_path, "url_details.json")
    with open(json_path, "w") as json_file:
        json.dump(url_details, json_file, indent=4)


def setup_tor_proxy():
    """Setup connection through Tor"""
    socks.set_default_proxy(socks.SOCKS5, "localhost", 9050)
    socket.socket = socks.socksocket
    public_ip = get_public_ip()
    print(f"Public IP as seen by other servers: {public_ip}")


def get_public_ip():
    """Retrieve the public IP as seen by other servers"""
    response = requests.get("http://httpbin.org/ip")
    return response.json()["origin"]


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


def process_url(url, base_download_path):
    try:
        download_path = create_subfolders(base_download_path, url)
        if download_path:
            url_data = download_media(url, download_path)
        else:
            url_data = {"url": url, "error": "No file was downloaded."}
    except Exception as e:
        url_data = {"url": url, "error": str(e)}

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
    return file_path


def download_media(url, file_path):
    """Download media file with support for partial content and timeouts"""
    max_retries = 3
    timeout_seconds = 20
    retry = 0

    while retry < max_retries:
        try:
            with requests.get(
                url, headers=HEADERS, timeout=timeout_seconds, stream=True
            ) as response:
                url_data = extract_url_data(url, response)
                if 200 <= response.status_code < 300:
                    write_to_file(file_path, response)
                    break
                else:
                    time.sleep(1)
                    retry += 1
        except Timeout:
            retry += 1

    return url_data


def extract_url_data(url, response: requests.Response):
    """Extract all relevant metadata from the response into a dictionary"""
    url_data = {
        "url": url,
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "file_size": int(response.headers.get("content-length", 0)),
    }

    return url_data


def write_to_file(file_path, response: requests.Response):
    """Write the response chunk-wise to a file"""
    with open(file_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        process_file(file_path)
    else:
        print("No file path provided as a command-line argument.")


if __name__ == "__main__":
    main()
