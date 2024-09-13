import time
import redis
from flask import Flask, jsonify
import os
import json
from celery import Celery
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Flask app
app = Flask(__name__)

# Redis configuration
cache = redis.Redis(host='redis', port=6379)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://redis:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://redis:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Path to ChromeDriver
CHROMEDRIVER_PATH = 'chromedriver'

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# Redis hit counter
def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return f'Hello World! I have been seen {count} times.\n'

@app.route('/getitems', methods=['GET'])
def get_items():
    # Check if results file exists and read the previous results
    if os.path.exists('results.json'):
        with open('results.json', 'r', encoding='utf-8') as file:
            old_results = json.load(file)
    else:
        old_results = []

    # Trigger the background task to fetch new data
    fetch_new_data.delay()

    # Return the old result immediately
    return jsonify({'old_results': old_results})

@celery.task
def fetch_new_data():
    # Initialize Chrome WebDriver in headless mode
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

    # URL of the YouTube search results page
    url = "https://www.youtube.com/results?search_query=how+to+4000+watch+time"
    
    # Open the URL
    driver.get(url)

    # Wait for elements to load (increase if necessary)
    driver.implicitly_wait(10)

    # Find all elements with the tag 'yt-formatted-string'
    yt_formatted_strings = driver.find_elements(By.TAG_NAME, 'yt-formatted-string')

    # Extract the text from each 'yt-formatted-string' element
    scraped_texts = [element.text for element in yt_formatted_strings]

    # Close the WebDriver
    driver.quit()

    # Save the new results to the file
    with open('results.json', 'w', encoding='utf-8') as file:
        json.dump(scraped_texts, file, ensure_ascii=False, indent=4)

