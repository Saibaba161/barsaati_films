from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pymongo
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient(MONGO_URI)
db = mongo_client["kothasaibaba460"]
collection = db["barsaati"]

# Initializing WebDriver
driver = webdriver.Chrome()

try:
    logging.info('Starting scraping')

    # Navigating the login page
    driver.get("https://x.com/i/flow/login")
    logging.info("Login page navigated")

    username = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "text")))
    username.send_keys(TWITTER_USERNAME)

    logging.info("Username entered")

    next_button = driver.find_element(By.XPATH, "//span[contains(text(),'Next')]")
    next_button.click()

    logging.info("Next clicked")

    password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password")))
    password.send_keys(TWITTER_PASSWORD)

    logging.info("Password entered")

    login_button = driver.find_element(By.XPATH, "//span[contains(text(),'Log in')]")
    login_button.click()

    logging.info("button clicked")

    WebDriverWait(driver, 40).until(EC.url_contains("https://x.com/home"))

    logging.info("Home successful")

    current_url = driver.current_url
    print(f"Current URL: {current_url}")

    # Extracting trending topics
    try:
        whats_happening_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1[text()='Trending now']/ancestor::section"))
        )
        logging.info("trending section found")

        trending_topics_elements = whats_happening_section.find_elements(By.XPATH, ".//div[@data-testid='trend']//span[contains(@class, 'css-1jxf684') and starts-with(text(), '#')]")
        trending_topics_text = [element.text for element in trending_topics_elements]
        logging.info(f"trending topics:{trending_topics_text}")

        # Processing trending topics
        top_trends = trending_topics_text[:5]

    except Exception as e:
        print(f"Error extracting trending topics: {e}")
        top_trends = []

    # Inserting the record into MongoDB
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

    logging.info(f"Inserting record:{record}")
    collection.insert_one(record)
    logging.info("Record inserted")

    if any(trend is not None for trend in top_trends):

        print("Record inserted into MongoDB")
    else:
        print("No trending topics found, record not inserted")

except Exception as e:
    logging.error(f"An error occurred: {e}")

finally:
    driver.quit()
    logging.info("Driver quit")
