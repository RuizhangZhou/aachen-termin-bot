from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

chrome_driver_path = "C:\Program Files\Google\Chrome\ChromeDriver\chromedriver.exe"  # 替换为你的ChromeDriver路径

chrome_options = Options()
chrome_options.add_argument("--headless")  # 无头模式

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("http://www.google.com")
print(driver.title)

driver.quit()
