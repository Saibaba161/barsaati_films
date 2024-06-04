from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pymongo
from datetime import datetime
import uuid
from flask import Flask, render_template, jsonify
from selenium.webdriver.chrome.options import Options

# MongoDB Atlas connection string
mongo_client = pymongo.MongoClient("mongodb+srv://kothasaibaba460:SaiBaba1610@cluster0.keygejh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["kothasaibaba460"]
collection = db["barsaati"]

# ProxyMesh
PROXY = "45.32.231.36:31280"

# Initialize WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % PROXY)
driver = webdriver.Chrome(options=chrome_options)

try:
    # Navigate to the login page
    driver.get("https://x.com/i/flow/login")

    # Wait for the username input field to be present and enter username
    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
    username.send_keys("giridhar_1610")
    print("Entered username")

    # Click the next button to proceed to the password field
    next_button = driver.find_element(By.XPATH,"//span[contains(text(),'Next')]")
    next_button.click()

    # Wait for the password input field to be present and enter password
    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
    password.send_keys("Girdhar@1610")

    # Click the login button
    login_button = driver.find_element(By.XPATH,"//span[contains(text(),'Log in')]")
    login_button.click()

    # Wait for the home page to load
    WebDriverWait(driver, 40).until(EC.url_contains("https://x.com/home"))

    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    driver.save_screenshot("homepage_screenshot.png")

    # Extract trending topics
    trends_section = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "css-175oi2r")))
    trending_topics = trends_section.find_elements(By.XPATH, ".//span[contains(@class, 'css-901oao')]")
    trending_topics_text = [topic.text for topic in trending_topics if topic.text.startswith('#')]

    # Process trending topics
    top_trends = trending_topics_text[:5]  # Get the top 5 trending topics

    # Insert the record into MongoDB
    record = {
        "_id": str(uuid.uuid4()),
        "trend1": top_trends[0] if len(top_trends) > 0 else None,
        "trend2": top_trends[1] if len(top_trends) > 1 else None,
        "trend3": top_trends[2] if len(top_trends) > 2 else None,
        "trend4": top_trends[3] if len(top_trends) > 3 else None,
        "trend5": top_trends[4] if len(top_trends) > 4 else None,
        "timestamp": datetime,
        "ip_address": driver.execute_script("return window.location.hostname")
    }
    collection.insert_one(record)

    input("Press enter to close the browser")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()

# Flask web application
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script')
def run_script():
    # Fetch the last record from MongoDB
    try:
        last_record = collection.find().sort([('_id', -1)]).limit(1)[0]
    except IndexError:
        last_record = None
    return render_template('result.html', record=last_record)

if __name__ == '__main__':
    app.run(debug=True)
