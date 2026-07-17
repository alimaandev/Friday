import os
from playwright.sync_api import sync_playwright

from core.logger import info

SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")
PROFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)


class BrowserManager:
    def __init__(self):
        self._context = None
        self._page = None
        self._launched = False
        self._pw = None

    def ensure(self):
        if not self._launched:
            self._launch()
        return self._page

    def get_page(self):
        self.ensure()
        return self._page

    def get_context(self):
        self.ensure()
        return self._context

    @property
    def is_launched(self) -> bool:
        return self._launched

    def _launch(self):
        self._pw = sync_playwright().start()
        self._context = self._pw.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--autoplay-policy=no-user-gesture-required",
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--disable-default-apps",
                "--disable-session-crashed-bubble",
                "--disable-restore-session-state",
            ],
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
        )

        self._context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)
        pages = self._context.pages
        self._page = pages[0] if pages else self._context.new_page()
        self._page.wait_for_load_state("domcontentloaded")
        self._page.bring_to_front()
        self._launched = True
        info("Browser launched")

    def close(self):
        if self._launched:
            try:
                self._pw.stop()
            except Exception:
                pass
            self._launched = False
            info("Browser closed")


_browser = BrowserManager()


def get_browser() -> BrowserManager:
    return _browser


def close_browser():
    _browser.close()
