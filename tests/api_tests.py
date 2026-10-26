"""HTTP checks for the same DaveAI pages the UI tests open.

These do not replace the browser tests. They fail fast when a URL, title, or
form id changes, and they do not need Chrome.
"""

import sys
import unittest
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.settings import BASE_URL

HOMEPAGE_TITLE = "AI-Native Automotive Intelligence Platform | DaveAI"


class TestDaveAIAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session = requests.Session()
        cls.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.session.close()

    def _get(self, path):
        response = self.session.get(BASE_URL + path, timeout=30)
        response.raise_for_status()
        return response

    def test_homepage_returns_expected_document(self):
        response = self._get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers.get("Content-Type", ""))
        self.assertIn(HOMEPAGE_TITLE, response.text)
        self.assertIn("Automotive Intelligence Across Every Function", response.text)
        self.assertIn("DaveAI_Logo", response.text)

    def test_contact_page_contains_the_form(self):
        response = self._get("/contact-us/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Get in Touch with DaveAI", response.text)
        self.assertIn('id="contact_us_form"', response.text)
        self.assertIn('placeholder="Email"', response.text)
        self.assertIn("Get in touch", response.text)

    def test_platform_page_contains_its_headline(self):
        response = self._get("/platform/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Discover the Power of DaveAI Platform", response.text)
        self.assertIn("Making user interactions Human-like and Empathetic!", response.text)

    def test_unknown_path_is_not_the_homepage(self):
        """A missing slug must not silently render the homepage document.

        The live site currently answers unknown paths with HTTP 200 and a
        different title (a soft 404). Accept either a real 404 or any page
        that is not the homepage.
        """
        response = self.session.get(
            BASE_URL + "/this-page-does-not-exist-daveai-qa/",
            timeout=30,
        )
        self.assertLess(response.status_code, 500)
        not_homepage = HOMEPAGE_TITLE not in response.text
        self.assertTrue(
            response.status_code == 404 or not_homepage,
            "Unknown URL unexpectedly returned the homepage",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
