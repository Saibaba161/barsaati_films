from flask import Flask, render_template, jsonify
import subprocess
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

app = Flask(__name__)

atlas_conn_string = MONGO_URI
client = MongoClient(atlas_conn_string)
db = client.kothasaibaba460
collection = db.barsaati

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_script')
def run_script():
    # Run the scraping script
    result = subprocess.run(['python', 'scraping.py'], capture_output=True, text=True)
    
    # Fetch the latest record from MongoDB
    last_record_cursor = collection.find().sort([('timestamp', -1)]).limit(1)
    last_record = list(last_record_cursor)
    
    if last_record:
        last_record = last_record[0]
    else:
        last_record = None

    return render_template('results.html', result=last_record)

@app.route('/get_results')
def get_results():
    last_record_cursor = collection.find().sort([('_id', -1)]).limit(1)
    last_record = list(last_record_cursor)
    
    if last_record:
        last_record = last_record[0]
    else:
        last_record = None

    return jsonify(last_record)

if __name__ == "__main__":
    app.run(debug=True)
