"""UI tests for https://www.iamdave.ai/

Four cases:
  1. Homepage loads with the expected title, logo, and h1.
  2. The Platform header link opens the platform page.
  3. The Book Demo button opens the demo page.
  4. The contact form accepts typed input and blocks an invalid email.

The contact test never submits a valid lead. DaveAI's form posts to their
sales inbox, so a "successful" submit from an automated run would be junk data.
"""

import sys
import unittest
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.driver_factory import create_driver
from tests.settings import EXPLICIT_WAIT
from tests.support import (
    click_visible_link,
    dismiss_overlays,
    open_path,
    text_of,
    visible_heading,
    wait_for_url,
)


class TestDaveAIUI(unittest.TestCase):
    def setUp(self):
        self.driver = None
        self.driver = create_driver()

    def tearDown(self):
        driver = getattr(self, "driver", None)
        if driver is None:
            return
        if self._failed():
            shot_dir = ROOT / "screenshots"
            shot_dir.mkdir(exist_ok=True)
            driver.save_screenshot(str(shot_dir / f"{self.id()}.png"))
        driver.quit()

    def _failed(self):
        outcome = getattr(self, "_outcome", None)
        result = getattr(outcome, "result", None)
        if result is None:
            return False
        return any(case is self for case, _exc in result.failures + result.errors)

    def test_homepage_loads_title_logo_and_heading(self):
        """The marketing homepage is up and shows the DaveAI brand and hero heading."""
        driver = self.driver
        open_path(driver, "/")
        dismiss_overlays(driver)

        self.assertIn("DaveAI", driver.title)
        self.assertIn("Automotive Intelligence", driver.title)

        heading = visible_heading(driver)
        self.assertEqual(
            text_of(heading.text),
            "Automotive Intelligence Across Every Function",
        )

        logo = WebDriverWait(driver, EXPLICIT_WAIT).until(
            lambda d: next(
                (
                    img
                    for img in d.find_elements(By.CSS_SELECTOR, "img[src*='DaveAI_Logo']")
                    if img.is_displayed()
                ),
                False,
            )
        )
        self.assertIn("DaveAI_Logo", logo.get_attribute("src"))
        parent_link = logo.find_element(By.XPATH, "./ancestor::a[1]")
        self.assertIn("iamdave.ai", parent_link.get_attribute("href") or "")

    def test_platform_navigation_opens_platform_page(self):
        """Header → Platform leaves the homepage and shows the platform headline."""
        driver = self.driver
        open_path(driver, "/")
        dismiss_overlays(driver)
        visible_heading(driver)

        click_visible_link(driver, "/platform/", "Platform")
        wait_for_url(driver, "/platform/")

        self.assertIn("DaveAI Platform", driver.title)
        self.assertIn(
            "Making user interactions Human-like and Empathetic!",
            text_of(visible_heading(driver).text),
        )

    def test_book_demo_button_opens_demo_page(self):
        """The Book Demo call-to-action opens the dedicated demo page."""
        driver = self.driver
        open_path(driver, "/")
        dismiss_overlays(driver)
        visible_heading(driver)

        click_visible_link(driver, "/book-demo/", "Book Demo")
        wait_for_url(driver, "/book-demo/")

        self.assertIn("Book Demo", driver.title)
        self.assertIn(
            "Ready to grow your revenue?",
            text_of(visible_heading(driver).text),
        )
        self.assertTrue(
            driver.find_element(By.CSS_SELECTOR, "form.elementor-form").is_displayed(),
            "Book Demo page should show its request form",
        )

    def test_contact_form_accepts_input_and_blocks_invalid_email(self):
        """Type into the contact form, then prove an invalid email cannot be submitted.

        Required fields on the live form are Email and Phone. This test fills
        the optional fields, checks that a bad email fails HTML5 validation,
        and clicks submit only while the email is empty so no lead is created.
        """
        driver = self.driver
        open_path(driver, "/contact-us/")
        dismiss_overlays(driver)

        self.assertIn("Get in Touch", driver.title)
        self.assertIn(
            "Let's Discuss Your Growth Goals",
            text_of(visible_heading(driver).text),
        )

        form = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.visibility_of_element_located((By.ID, "contact_us_form"))
        )
        name = form.find_element(By.CSS_SELECTOR, "[placeholder='Name']")
        email = form.find_element(By.CSS_SELECTOR, "[placeholder='Email']")
        company = form.find_element(By.CSS_SELECTOR, "[placeholder='Company name']")
        message = form.find_element(By.CSS_SELECTOR, "textarea")

        name.send_keys("Alex Rivera")
        company.send_keys("Example Motors")
        message.send_keys("Automated UI check. Please ignore.")

        self.assertEqual(name.get_attribute("value"), "Alex Rivera")
        self.assertEqual(company.get_attribute("value"), "Example Motors")
        self.assertIn("Please ignore", message.get_attribute("value"))

        email.send_keys("not-an-email")
        email_is_valid = driver.execute_script(
            "return arguments[0].checkValidity();", email
        )
        self.assertFalse(
            email_is_valid,
            "A value that is not an email address must fail field validation",
        )

        email.clear()
        self.assertEqual(email.get_attribute("value"), "")
        submit = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.assertEqual(text_of(submit.text).casefold(), "get in touch")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", submit)
        submit.click()

        still_invalid = driver.execute_script(
            "return arguments[0].checkValidity();", email
        )
        self.assertFalse(still_invalid, "Empty required email must block submit")
        self.assertIn("/contact-us", driver.current_url)
        success = driver.find_elements(By.CSS_SELECTOR, ".elementor-message-success")
        self.assertFalse(
            any(item.is_displayed() for item in success),
            "Invalid submit must not show a success message",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
