"""
Simple Flask app to receive Salesforce data and write it to Kafka.
"""

import os
from flask import Flask, jsonify, request

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


@app.route('/sf-data', methods=['POST'])
def sf_data():
    """
    Receives serialized sObject data. Intended to be called from an asynchronous Apex.

    Test it with something like:
    curl -H "Content-Type: application/json" -X POST -d '{"username":"xyz","password":"xyz"}' http://127.0.0.1:5000/sf-data
    """
    # TODO: verify origin of request using the secret key.
    error = None
    if request.method == 'POST':
        data = request.get_json()
        # TODO: write to Kafka
        return str(data)

@app.route('/')
def home():
    """
    Default home page.
    """
    return('hey hey')


if __name__ == '__main__':
    app.run(debug=True)
