"""Shared Playwright launch for tools/qa (this machine's installed browser build; edit the paths elsewhere).
Every script takes the folder for its results as its first argument, e.g. tools/qa/ix_suite.py <scratch>."""
HEADLESS = r"C:\Users\viraa\AppData\Local\ms-playwright\chromium_headless_shell-1243\chrome-headless-shell-win64\chrome-headless-shell.exe"
FULL = r"C:\Users\viraa\AppData\Local\ms-playwright\chromium-1243\chrome-win64\chrome.exe"
BASE = "http://127.0.0.1:8080/"


def launch(p, full=False):
    return p.chromium.launch(executable_path=FULL if full else HEADLESS)
