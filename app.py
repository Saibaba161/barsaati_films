from flask import Flask, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
import pymongo
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

app = Flask(__name__)

atlas_conn_string = MONGO_URI
client = MongoClient(atlas_conn_string)
db = client.kothasaibaba460
collection = db.barsaati

def scrape_trending_topics():
    # Install Chrome WebDriver using WebDriverManager
    ChromeDriverManager(version="92.0.4515.43").install()
    # Initialize WebDriver
    driver = webdriver.Chrome()
    
    try:
        driver.get("https://twitter.com/i/flow/login")

        username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
        username.send_keys(TWITTER_USERNAME)

        next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
        next_button.click()

        password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
        password.send_keys(TWITTER_PASSWORD)

        login_button = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
        login_button.click()

        WebDriverWait(driver, 40).until(EC.url_contains("https://twitter.com/home"))

        current_url = driver.current_url
        print(f"Current URL: {current_url}")

        whats_happening_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Trending now']/ancestor::section"))
        )

        trending_topics_elements = whats_happening_section.find_elements(By.XPATH, ".//div[@data-testid='trend']//span[contains(@class, 'css-1jxf684') and starts-with(text(), '#')]")
        trending_topics_text = [element.text for element in trending_topics_elements]

        top_trends = trending_topics_text[:5]

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
        # Insert record into MongoDB collection
        collection.insert_one(record)
        if any(trend is not None for trend in top_trends):
            print("Record inserted into MongoDB")
        else:
            print("No trending topics found, record not inserted")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script')
def run_script():
    # Call the scraping function
    scrape_trending_topics()
    last_record = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])

    if last_record:
        return render_template('results.html', result=last_record)
    else:
        return "No data found" 

@app.route('/get_results')
def get_results():
    last_record = collection.find_one(sort=[('timestamp', pymongo.DESCENDING)])

    if last_record:
        return jsonify(last_record)
    else:
        return jsonify({"error": "No data found"})

if __name__ == "__main__":
    app.run(debug=True)