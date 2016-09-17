"""
Simple Flask app to receive Salesforce data and write it to Kafka.
"""

import kafka_helper
import os
from flask import Flask, abort, request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')

CHATTER_KAFKA_TOPIC = 'chatter'
PRODUCER = kafka_helper.get_kafka_producer()


@app.route('/sf-data', methods=['POST'])
def sf_data():
    """
    Receives serialized sObject data and writes selected fields to Kafka.
    Intended to be called from an asynchronous Apex.
    """
    if not verify_secret_key(request):
        abort(401)

    if request.method == 'POST':
        filtered_sobject_list = filter_sobject_list(request.get_json() or [])
        for sobject in filtered_sobject_list:
            write_to_kafka(key=str(sobject['ParentId']), value=sobject)
        return str(filtered_sobject_list)


def verify_secret_key(request):
    # TODO: verify origin of request using the secret key.
    return True


def filter_sobject_list(sobject_list):
    """
    Takes a list of FeedItem/FeedComment and returns the list with only the fields that we care about,
    with normalized keys.
    """
    sobject_type = sobject_list[0]['attributes']['type'] if sobject_list else None
    fields = ('Body' if sobject_type == 'FeedItem' else 'CommentBody',
              'Id' if sobject_type == 'FeedItem' else 'FeedItemId',
              'ParentId',
              'CreatedById',
              'CreatedDate')
    filtered_sobject_list = [ {key: x[key] for key in fields} for x in sobject_list ]

    for sobject in filtered_sobject_list:
        # Normalize all body fields to be called "Body".
        if 'CommentBody' in sobject:
            sobject['Body'] = sobject.pop('CommentBody')
        # Normalize all feed item ID fields to be called "FeedItemId".
        if 'FeedItemId' not in sobject:
            sobject['FeedItemId'] = sobject.pop('Id')

    return filtered_sobject_list


def write_to_kafka(key, value):
    PRODUCER.send(CHATTER_KAFKA_TOPIC, key=key, value=value)
    PRODUCER.flush()


if __name__ == '__main__':
    app.run(debug=True)
