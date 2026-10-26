"""Small helpers shared by the UI tests. Locators stay in the tests themselves."""

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tests.settings import BASE_URL, EXPLICIT_WAIT


def text_of(value):
    return " ".join((value or "").replace("\xa0", " ").split())


def open_path(driver, path):
    if not path.startswith("/"):
        path = "/" + path
    driver.get(BASE_URL + path)


def dismiss_overlays(driver):
    """Click a cookie/popup close control if one is actually on screen."""
    selectors = [
        ".elementor-popup-modal .dialog-close-button",
        "button[aria-label='Close']",
        "button[aria-label='close']",
        ".cky-btn-accept",
        "#onetrust-accept-btn-handler",
        ".cookie-notice .cn-set-cookie",
    ]
    for selector in selectors:
        for element in driver.find_elements(By.CSS_SELECTOR, selector):
            try:
                if element.is_displayed():
                    element.click()
            except Exception:
                continue


def _first_visible_link(driver, href_part, text_part):
    wanted = text_part.casefold()
    for element in driver.find_elements(By.CSS_SELECTOR, "a[href]"):
        href = element.get_attribute("href") or ""
        if href_part not in href:
            continue
        label = text_of(element.text).casefold()
        if wanted not in label:
            continue
        if element.is_displayed():
            return element
    return False


def click_visible_link(driver, href_part, text_part):
    """Click the on-screen link. Header and mobile menus both exist in the DOM."""
    last_error = None
    for _ in range(3):
        try:
            element = WebDriverWait(driver, EXPLICIT_WAIT).until(
                lambda d: _first_visible_link(d, href_part, text_part)
            )
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", element
            )
            dismiss_overlays(driver)
            try:
                element.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", element)
            return
        except StaleElementReferenceException as exc:
            last_error = exc
    raise AssertionError(f"Could not click a visible '{text_part}' link") from last_error


def wait_for_url(driver, part):
    WebDriverWait(driver, EXPLICIT_WAIT).until(EC.url_contains(part))


def visible_heading(driver):
    return WebDriverWait(driver, EXPLICIT_WAIT).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
