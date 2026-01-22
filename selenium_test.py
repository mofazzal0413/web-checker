from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def run_selenium_smoke_test(url):
    result = {"url": url}

    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        title = driver.title.strip()

        if title:
            result["status"] = "PASS"
            result["message"] = f"Selenium OK — Title found: '{title}'"
        else:
            result["status"] = "FAIL"
            result["message"] = "Page loaded but title is empty"

        driver.quit()

    except Exception as e:
        result["status"] = "FAIL"
        result["message"] = f"Selenium error: {str(e)}"

    return result
