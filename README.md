# DaveAI UI tests

Python UI tests for [https://www.iamdave.ai/](https://www.iamdave.ai/). The site is DaveAI's marketing site for an automotive AI platform. The suite checks that the homepage, main navigation, and contact form behave. It does **not** send a real demo request.

## What is covered

| Test | File | What it checks |
| --- | --- | --- |
| Homepage loads | `tests/ui_tests.py` | Title contains DaveAI and "Automotive Intelligence". The hero h1 is "Automotive Intelligence Across Every Function". The DaveAI logo image is visible and links back to the site. |
| Platform navigation | `tests/ui_tests.py` | From the homepage, the visible **Platform** header link opens `/platform/` and the h1 "Making user interactions Human-like and Empathetic!". |
| Book Demo | `tests/ui_tests.py` | The visible **Book Demo** button opens `/book-demo/`, the heading "Ready to grow your revenue?", and the demo form. |
| Contact form | `tests/ui_tests.py` | On `/contact-us/`, name, company, and message accept typed text. `not-an-email` fails email validation. Submit with an empty email stays on the page and does not show a success message. |
| HTTP smoke | `tests/api_tests.py` | Homepage, contact, and platform URLs return HTML that still contains those titles and the contact form. An unknown path is not a copy of the homepage. |

## Project layout

```text
iamdave-ui-tests/
  run_tests.py            # launch this from Eclipse (runs UI + API)
  requirements.txt
  pytest.ini
  .project                # Eclipse / PyDev project metadata
  .pydevproject
  tests/
    ui_tests.py           # Selenium tests
    api_tests.py          # requests checks (no browser)
    driver_factory.py     # Chrome options, setup of the WebDriver
    support.py            # waits, clicks, popup dismissal
    settings.py           # BASE_URL and the explicit-wait timeout
```

## Design choices

- **Selenium, not Playwright.** The brief allows either. Selenium talks to Chrome through ChromeDriver, which is what Eclipse lab machines usually have, and Selenium Manager downloads a matching driver on the first run. No separate driver install step.
- **unittest, also runnable by pytest.** `unittest` is what PyDev runs when you choose *Run As → Python unit-test*. `pytest.ini` is included so `pytest -v` works from a terminal as well.
- **One browser per UI test.** `setUp` starts Chrome and `tearDown` quits it, so a single method can be launched from Eclipse without depending on the others. A failed test saves a screenshot under `screenshots/`.
- **Explicit waits only.** The pages are Elementor / WordPress and load a lot of third-party script. Assertions wait up to 25 seconds for a visible element or URL. There is no implicit wait, because stacking the two makes failures look hung.
- **Page load strategy `eager`.** Tests only need the HTML (title, headings, links, form). They do not wait for every analytics pixel.
- **Visible-link clicks.** The header is rendered twice (desktop and mobile). Tests click the link that is actually displayed, matched by href and label, so a hidden copy of "Platform" is ignored.
- **The contact form is not submitted with valid data.** Email and phone are required and the form posts to DaveAI. The test types into the fields and only clicks submit while the email is empty, then asserts HTML5 `checkValidity()` is false. That covers "input field interaction" without creating a sales lead.
- **Locators prefer the form's placeholders and the logo file name.** Those are stable on the current site. Navigation uses the real href (`/platform/`, `/book-demo/`) plus the visible label, because the menu markup is duplicated.
- **API tests are a separate, browser-free layer.** They catch a down site or a renamed title in a couple of seconds. They are not a substitute for the Selenium cases.

## Dependencies

- Python 3.10 or newer
- Google Chrome (current stable is fine)
- Packages in `requirements.txt`:
  - `selenium` — WebDriver and ChromeDriver via Selenium Manager
  - `requests` — the HTTP checks
  - `pytest` — optional, if you prefer pytest over unittest

ChromeDriver does not need to be downloaded by hand.

## Run from a terminal

From this folder:

```bash
python -m pip install -r requirements.txt
python run_tests.py
```

Useful variants:

```bash
# UI tests only
python tests/ui_tests.py

# HTTP checks only (no Chrome window)
python tests/api_tests.py

# pytest
pytest -v

# watch the browser on a machine that would otherwise run headless
# Windows and macOS already show Chrome unless you set HEADLESS=1
HEADLESS=0 python run_tests.py
```

On Windows PowerShell, set the variable for one command with:

```powershell
$env:HEADLESS = "1"
python run_tests.py
```

### Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `BASE_URL` | `https://www.iamdave.ai` | Point the same tests at a staging host if you have one. |
| `HEADLESS` | on for Linux with no `DISPLAY`; off on Windows and macOS | `1` hides Chrome, `0` shows it. |
| `EXPLICIT_WAIT` | `25` | Seconds to wait for an element or URL. |
| `CHROME_BINARY` | Chrome on PATH | Full path to `chrome.exe` if Selenium cannot find the install. |
| `CHROME_NO_SANDBOX` | on only when running as root | Set to `1` if Chrome exits immediately inside a locked-down lab image. |

## Run in Eclipse

These files already include Eclipse project metadata (`.project`, `.pydevproject`). You need the PyDev plugin, because stock Eclipse does not run Python.

1. Install Python 3.10+ from [python.org](https://www.python.org/downloads/). On the installer, check **Add python.exe to PATH**. Confirm in a command prompt: `python --version`.
2. Install [Google Chrome](https://www.google.com/chrome/).
3. In Eclipse: **Help → Eclipse Marketplace**, search **PyDev**, install it, and restart Eclipse.
4. **Window → Preferences → PyDev → Interpreters → Python Interpreter → New**. Choose the `python.exe` you just installed. Let Eclipse load the system libs.
5. With that interpreter selected, open **Packages** (or use a terminal) and install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

   Run that command in the `iamdave-ui-tests` folder. If Eclipse has no terminal view, use **Window → Show View → Terminal**, or run the same command in Command Prompt.
6. **File → Import → General → Existing Projects into Workspace → Next**. Choose the `iamdave-ui-tests` folder (the one that contains `.project`). Finish.
7. If Eclipse says the PyDev nature is missing, install PyDev and re-open the project. The interpreter must be the one from step 4 (**Project → Properties → PyDev - Interpreter**).
8. Run everything: right-click `run_tests.py` → **Run As → Python Run**. The console lists each test and prints `OK` at the end.
9. Run a single case: open `tests/ui_tests.py`, click inside the test method, then **Run As → Python unit-test**. You can also right-click the file → **Run As → Python Run**, which uses the `unittest.main()` block at the bottom of the file.

Working directory for the launch must be the project folder (PyDev's default). Screenshots from failures are written to `screenshots/` inside the project.

To force a visible browser from an Eclipse run configuration: **Run → Run Configurations → Python Run → Environment → New**, name `HEADLESS`, value `0`.

## Notes about the live site

Assertions match the public site as checked on 24 October 2026:

- Homepage title: `AI-Native Automotive Intelligence Platform | DaveAI`
- Homepage h1: `Automotive Intelligence Across Every Function`
- Logo: `DaveAI_Logo.svg`
- Platform h1: `Making user interactions Human-like and Empathetic!`
- Book Demo h1: `Ready to grow your revenue?`
- Contact form id: `contact_us_form`. The submit control's HTML label is `Get in touch`; CSS renders it as `GET IN TOUCH`, so the UI test compares the label case-insensitively.

If DaveAI redesigns a heading, update the expected string in the matching test rather than loosening the assertion to "page contains DaveAI".
