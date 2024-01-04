from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time, pyotp
from datetime import datetime, timedelta
import requests
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

#### Load Config Variables ####
ENV = 'production'
amazon_vendor_email = config.get(ENV,'amazon_vendor_email')
amazon_vendor_password = config.get(ENV,'amazon_vendor_password')
otp_creation_secret_key = config.get(ENV,'otp_creation_secret_key')
#### Load Config Variables ####

# Initialize Chrome WebDriver with ChromeDriver executable path and options
service = Service('chromedriver.exe')
options = Options()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=service)

# Open the login page
driver.get("https://vendorcentral.amazon.com/home/vc")

# Wait for the username field to be present
username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
username.clear()
username.send_keys(amazon_vendor_email)
time.sleep(2)

# Wait for the password field to be present
password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
password.clear()
password.send_keys(amazon_vendor_password)
time.sleep(2)

# Find and click the login button
elem = driver.find_element(By.XPATH, "//*[@id='signInSubmit']")
elem.click()
time.sleep(2)

# Wait for the OTP field to be present (you need to replace 'auth-mfa-otpcode' with the actual ID of the OTP field)
otp_field = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.ID, "auth-mfa-otpcode")))

# Generate OTP using pyotp (you need to replace 'your_secret_key' with your actual secret key)
totp = pyotp.TOTP(otp_creation_secret_key)
generated_otp = totp.now()

# Enter the generated OTP into the OTP field
otp_field.clear()
otp_field.send_keys(generated_otp)
time.sleep(3)

# Click the sign-in button
elem = driver.find_element(By.XPATH, "//*[@id='auth-signin-button']")
elem.click()

# Add a delay to ensure the redirection has occurred before navigating to the desired URLs
time.sleep(3)

# Calculate the date three days ago
three_days_ago = datetime.now() - timedelta(days=3)
formatted_date = three_days_ago.strftime("%Y-%m-%d")

# Build the dynamic URL with the calculated date for Daily
dynamic_url = f"https://vendorcentral.amazon.com/retail-analytics/dashboard/sales?daily-day={formatted_date}&submit=true&time-period=daily"

# Open the dynamic URL
driver.get(dynamic_url)
time.sleep(3)

csv = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div[2]/div[1]/div[2]/div/div[1]/kat-button-group/kat-button[1]')
csv.click()

# Click on "View and manage your downloads" hyperlink
hyperlink_xpath = '#root > div > div > div.ltr-ls0ln > div > div.ltr-1bvc4cc > div:nth-child(1) > a'
hyperlink = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, hyperlink_xpath)))
hyperlink.click()

refresh_class = 'ltr-4mlr47'
refresh_sidebar = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, refresh_class)))
refresh_sidebar.click()

time.sleep(25)

download_csv_report_xpath = '#root > div > div.ltr-1odx2my > div.ltr-6yaw4i > kat-table > kat-table-body > kat-table-row:nth-child(1) > kat-table-cell:nth-child(2) > a'
download_link = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR,download_csv_report_xpath)))
download_link.click()
time.sleep(10)

# Close the browser
driver.close()
driver.quit()