from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
from datetime import datetime
import uuid
from flask import Flask, render_template

# MongoDB Atlas connection string
mongo_client = pymongo.MongoClient("mongodb+srv://kothasaibaba460:SaiBaba1610@cluster0.keygejh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["kothasaibaba460"]
collection = db["barsaati"]

# Initialize WebDriver
driver = webdriver.Chrome()

try:
    # Navigate to the login page
    driver.get("https://x.com/i/flow/login")

    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
    username.send_keys("giridhar_1610")

    next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
    next_button.click()

    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
    password.send_keys("Girdhar@1610")

    login_button = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
    login_button.click()

    WebDriverWait(driver, 40).until(EC.url_contains("https://x.com/home"))

    current_url = driver.current_url
    print(f"Current URL: {current_url}")
    driver.save_screenshot("homepage_screenshot.png")

    # Extract trending topics
    try:
        whats_happening_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Trending now']/ancestor::section"))
        )

        trending_topics_elements = whats_happening_section.find_elements(By.XPATH, ".//div[@data-testid='trend']//span[contains(@class, 'css-1jxf684') and starts-with(text(), '#')]")
        trending_topics_text = [element.text for element in trending_topics_elements]

        # Process trending topics
        top_trends = trending_topics_text[:5]
    except Exception as e:
        print(f"Error extracting trending topics: {e}")
        top_trends = []

    # Insert the record into MongoDB
    record = {
        "_id": str(uuid.uuid4()),
        "trend1": top_trends[0] if len(top_trends) > 0 else None,
        "trend2": top_trends[1] if len(top_trends) > 1 else None,
        "trend3": top_trends[2] if len(top_trends) > 2 else None,
        "trend4": top_trends[3] if len(top_trends) > 3 else None,
        "trend5": top_trends[4] if len(top_trends) > 4 else None,
        "timestamp": datetime.now(),
        "ip_address": driver.execute_script("return window.location.hostname")
    }
    print("Record to be inserted:", record)

    if any(trend is not None for trend in top_trends):
        collection.insert_one(record)
        print("Record inserted into MongoDB")
    else:
        print("No trending topics found, record not inserted")

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
    # Fetching the last record from MongoDB
    try:
        last_record = collection.find().sort([('timestamp', -1)]).limit(1)[0]
    except IndexError:
        last_record = None
    return render_template('result.html', record=last_record)

if __name__ == '__main__':
    app.run(debug=True)
