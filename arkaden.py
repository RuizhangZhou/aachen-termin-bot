import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Bot
from dotenv import load_dotenv
import schedule

# 加载环境变量
load_dotenv()

# Telegram Bot的Token和频道ID
TOKEN = os.getenv("TOKEN")
ARKADEN_CHANNEL_ID = '@arkadentermin'

# 配置日志
logging.basicConfig(level=logging.INFO)

# 初始化Telegram Bot
bot = Bot(token=TOKEN)

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")  # 新版无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--disable-software-rasterizer")  # 禁用软渲染器
    chrome_options.add_argument("--disable-popup-blocking")  # 禁用弹窗拦截
    chrome_options.add_argument("--disable-notifications")  # 禁用通知
    chrome_options.add_argument("--disable-extensions")  # 禁用扩展
    chrome_options.add_argument("--disable-infobars")  # 禁用信息栏
    chrome_options.add_argument("--no-first-run")  # 禁用首次运行设置

    # 使用 webdriver_manager 自动下载和设置 ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver



def check_appointments():
    driver = initialize_driver()  # 每次运行时重新初始化驱动
    try:
        # 打开目标页面
        url = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
        driver.get(url)
        
        # 等待页面加载
        wait = WebDriverWait(driver, 20)

        # 第一步：展开h3，找到并点击Abholung选项
        logging.info("Trying to expand 'Abholung' section...")
        abholung_h3 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "h3[aria-controls='content_concerns_accordion-454']")))
        driver.execute_script("arguments[0].scrollIntoView();", abholung_h3)
        abholung_h3.click()

        # 第二步：点击“增加数量”按钮
        logging.info("Clicking the 'plus' button for Abholung...")
        increase_button = wait.until(EC.element_to_be_clickable((By.ID, "button-plus-299")))
        driver.execute_script("arguments[0].scrollIntoView();", increase_button)
        increase_button.click()

        # 第三步：点击"weiter"按钮
        logging.info("Clicking 'Weiter' button...")
        weiter_button = wait.until(EC.element_to_be_clickable((By.ID, "WeiterButton")))
        driver.execute_script("arguments[0].scrollIntoView();", weiter_button)
        weiter_button.click()

        # 第四步：处理弹出框，点击"OK"按钮
        logging.info("Handling confirmation pop-up...")
        ok_button = wait.until(EC.element_to_be_clickable((By.ID, "OKButton")))
        driver.execute_script("arguments[0].scrollIntoView();", ok_button)
        ok_button.click()

        # 第五步：在下一个页面中选择Ausländeramt Aachen Arkaden
        logging.info("Selecting 'Aachen Arkaden' location...")
        arkaden_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='select_location'][value='Ausländeramt Aachen - Aachen Arkaden, Trierer Straße 1, Aachen auswählen']")))
        driver.execute_script("arguments[0].scrollIntoView();", arkaden_button)
        arkaden_button.click()

        # 等待跳转到最后的预约页面
        time.sleep(3)
        
        # 第六步：检查页面内容是否包含“Kein freier Termin verfügbar”
        logging.info("Checking for appointment availability...")
        page_source = driver.page_source
        if "Kein freier Termin verfügbar" in page_source:
            logging.info("No appointments available.")
        else:
            # 如果有可用的预约，发送Telegram通知
            logging.info("Appointments available!")
            bot.send_message(chat_id=ARKADEN_CHANNEL_ID, text="Appointments available at Aachen Arkaden!")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        driver.quit()  # 确保浏览器每次运行后都关闭

def job():
    check_appointments()

if __name__ == '__main__':
    schedule.every(1).minutes.do(job)  # 每1分钟运行一次

    while True:
        schedule.run_pending()  # 检查是否有任务需要运行
        time.sleep(10)  # 每1秒检查一次
