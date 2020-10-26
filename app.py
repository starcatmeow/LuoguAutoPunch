from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from PIL import Image
import tensorflow as tf
import os
import time
import re

LUOGU_LOGIN_URL = "https://www.luogu.com.cn/auth/login"
LUOGU_HOME_URL = "https://www.luogu.com.cn"

try:
    LUOGU_USERNAME = os.environ['LUOGU_USERNAME']
    LUOGU_PASSWORD = os.environ['LUOGU_PASSWORD']
except:
    print('请在环境变量中设置 LUOGU_USERNAME, LUOGU_PASSWORD ！', flush=True)
    exit(4)

def login(driver):
    driver.get(LUOGU_LOGIN_URL)
    time.sleep(5)
    inputs = driver.find_elements_by_xpath("//input[@placeholder]")
    inputs[0].send_keys(LUOGU_USERNAME)
    inputs[1].send_keys(LUOGU_PASSWORD)
    captcha = driver.find_element_by_xpath("//img[contains(@src,'captcha')]")
    driver.save_screenshot('captcha.png')

    left = captcha.location['x']
    top = captcha.location['y']
    right = captcha.location['x'] + captcha.size['width']
    bottom = captcha.location['y'] + captcha.size['height']

    im = Image.open('captcha.png') 
    im = im.crop((left, top, right, bottom))
    im.save('captcha.png')

    with open(r"captcha.png","rb") as f:
        captcha_bytes = f.read()
    with tf.device('/CPU:0'):
        import muggle_ocr
        sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
    captcha_text = sdk.predict(image_bytes=captcha_bytes)
    print("验证码: "+captcha_text, flush=True)

    time.sleep(1)
    inputs[2].send_keys(captcha_text)

    login_button = driver.find_element_by_xpath("//button[contains(@class,'login')]")
    login_button.send_keys(Keys.ENTER)
    
def check(driver):
    if driver.current_url != LUOGU_LOGIN_URL:
        print('登录成功', flush=True)
        return True
    else:
        print('登录失败', flush=True)
        return False

def punch(driver):
    driver.get(LUOGU_HOME_URL)
    time.sleep(5)
    try:
        punch = driver.find_element_by_link_text("点击打卡")
        driver.execute_script("arguments[0].click();", punch)
        print('打卡成功', flush=True)
        return True
    except:
        print('已经打过卡了', flush=True)
        return False

def get_result(driver):
    time.sleep(5)
    try:
        result_origin = driver.find_element_by_xpath("//span[contains(@class,'lg-punch-result')]").text
        result = re.match(r'§ (.*) §',result_origin).group(1)
        day = driver.find_element_by_xpath("//div[contains(@class,'am-u-sm')]//strong").text
        print("已连续打卡 {} 天，今日运势：{}".format(day,result), flush=True)
        return True
    except:
        print("无法获取打卡结果", flush=True)
        return False

chrome_options = Options()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)
login(driver)
time.sleep(10)
errorcnt = 0
while check(driver) == False:
    errorcnt += 1
    print('重试中...', flush=True)
    if errorcnt >= 5:
        print('错误：无法登录', flush=True)
        driver.quit()
        exit(1)
    login(driver)
    time.sleep(10)
errorcnt = 0
while punch(driver) == False:
    if get_result(driver) == False:
        errorcnt += 1
        if errorcnt >= 5:
            print('错误：无法打卡', flush=True)
            driver.quit()
            exit(3)
        print('重试中...', flush=True)
    else:
        driver.quit()
        exit(0)
get_result(driver)
driver.quit()
exit(0)
