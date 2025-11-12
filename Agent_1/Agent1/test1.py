from playwright.sync_api import sync_playwright, Playwright
import time

def run(playwright: Playwright):
    chromium = playwright.firefox # or "firefox" or "webkit".
    browser = chromium.launch(headless=False,           
    slow_mo=1000,            
    )
    page = browser.new_page()
    page.goto("https://www.youtube.com/")
    time.sleep(180)
    # other actions...
    browser.close()

with sync_playwright() as playwright:
    run(playwright)