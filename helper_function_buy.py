from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from dotenv import load_dotenv
import os
from data import buy_data

print("Data from Google Sheets:", buy_data)

# Load credentials from .env file
load_dotenv()
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
PIN = os.getenv("PIN")


def get_driver():
    """Configure headless Chrome for Railway (containerized) environment."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")          # Headless mode (no GUI)
    chrome_options.add_argument("--no-sandbox")            # Required on Railway
    chrome_options.add_argument("--disable-dev-shm-usage") # Prevents /dev/shm issues
    chrome_options.add_argument("--disable-gpu")           # No GPU in containers
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Railway/Linux: chromedriver is installed via apt, no binary path needed
    # locally on Windows/Mac you can keep Service(executable_path=...)
    service = Service()  # uses chromedriver from PATH
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Setup driver
driver = get_driver()
wait = WebDriverWait(driver, 10)

driver.get("https://web.bmatrade.com/webterminal/BMALoginView")
time.sleep(2)

user_id_field = wait.until(
    EC.presence_of_element_located((By.ID, "txtUserID"))
)
user_id_field.clear()
user_id_field.send_keys(USER_ID)
print("User ID entered!")
time.sleep(1)

password_field = wait.until(
    EC.presence_of_element_located((By.ID, "txtPassword"))
)
password_field.clear()
password_field.send_keys(PASSWORD)
print("Password entered!")
time.sleep(1)

login_button = wait.until(
    EC.element_to_be_clickable((By.ID, "submitButton"))
)
login_button.click()
print("Login clicked!")
time.sleep(4)


def buy(driver, wait, symbol):
    symbol_field = wait.until(
        EC.presence_of_element_located((By.ID, "symbol-list-combo-inputEl"))
    )
    symbol_field.clear()
    symbol_field.send_keys(symbol + "-REG-KSE")
    print(f"Symbol {symbol} entered!")
    time.sleep(2)

    symbol_field.send_keys(Keys.ENTER)
    print(f"Enter pressed for {symbol}!")
    time.sleep(1)

    volume_field = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//tr[@id='txtVolums-inputRow']//input")
        )
    )
    volume_field.clear()
    volume_field.send_keys("1")
    print("Volume 1 entered!")
    time.sleep(1)

    order_type_field = wait.until(
        EC.element_to_be_clickable((By.ID, "ddlOrderType-inputEl"))
    )
    order_type_field.click()
    print("Clicked order type field!")
    time.sleep(1)

    market_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//li[contains(@class,'x-boundlist-item') and text()='MARKET']")
        )
    )
    market_option.click()
    print("Selected MARKET!")
    time.sleep(1)

    buy_button = wait.until(
        EC.element_to_be_clickable((By.ID, "buyOrderButton-btnEl"))
    )
    buy_button.click()
    print(f"BUY order placed for {symbol}!")
    time.sleep(6)

     # Enter "PIN" in Trading Pin Verification dialog
    '''pin_field = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//tr[@id='OrderPinCodeField-inputRow']//input")
        )
    )
    pin_field.clear()
    pin_field.send_keys(PIN)
    print("PIN entered!")
    time.sleep(1)

    # Click The Trade Button
    trade_button = wait.until(
     EC.element_to_be_clickable((By.ID, "button-1196-btnEl"))
        )
    trade_button.click()
    print("Trade button clicked!")
    time.sleep(6)'''
    



try:
    for symbol, suggestion in buy_data.items():
        if suggestion.upper() == "BUY":
            buy(driver, wait, symbol)
finally:
    driver.quit()
    print("Driver closed.")
