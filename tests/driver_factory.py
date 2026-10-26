"""Creates a Chrome WebDriver.

Selenium Manager (shipped inside Selenium 4.6+) downloads a ChromeDriver build
that matches the installed Google Chrome, so Eclipse users do not have to
place chromedriver.exe on PATH themselves.
"""

import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def _flag(name, default):
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _running_as_root():
    geteuid = getattr(os, "geteuid", None)
    try:
        return bool(geteuid and geteuid() == 0)
    except OSError:
        return False


def _headless_by_default():
    """Show the window on a desktop. Hide it on a Linux box with no display."""
    if os.getenv("DISPLAY") or sys.platform in {"win32", "darwin"}:
        return False
    return True


def create_driver():
    options = Options()
    binary = os.getenv("CHROME_BINARY")
    if binary:
        options.binary_location = binary

    # "eager" returns after DOMContentLoaded. The DaveAI pages are heavy
    # (analytics, lazy scripts) and the content these tests need is in the HTML.
    options.page_load_strategy = "eager"

    if _flag("HEADLESS", _headless_by_default()):
        options.add_argument("--headless=new")

    options.add_argument("--window-size=1440,1000")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--lang=en-US")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    # Required when Chrome runs as root (containers). Harmless to leave off
    # on a normal Windows Eclipse install; set CHROME_NO_SANDBOX=1 if Chrome
    # refuses to start in a locked-down lab image.
    if _running_as_root() or _flag("CHROME_NO_SANDBOX", False):
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    # Explicit waits only. An implicit wait would stack on top of them and
    # make failures very slow.
    driver.implicitly_wait(0)
    return driver
