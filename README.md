# df16-sf-kafka-demo

Demo code for the Dreamforce 2016 session [Analyzing Salesforce Data with Heroku, Kafka, and Connect](https://success.salesforce.com/Sessions?eventId=a1Q3000000qQOd9#/session/a2q3A000000LBeAQAW).

The demo consists of the following parts:
1. A [script](https://github.com/alouie-sfdc/chatter-data-pump) that continuously posts to Salesforce Chatter.
1. Apex triggers that send Salesforce Chatter data to a Heroku app using an asynchronous HTTP callout.
1. A producer (the Heroku app), which writes a subset of the data to Apache Kafka on Heroku.
1. A consumer that reads from Kafka and performs sentiment analysis.

## Heroku setup
This creates the app that receives REST requests from Salesforce and writes to Kafka.

1. `heroku apps:create MY-APP-NAME`
1. `heroku addons:create heroku-kafka:beta-standard-0`
1. `heroku kafka:wait`
1. `heroku kafka:topics:create chatter`
1. Deploy this repo to your app.


## Salesforce setup
1. Add the Apex class and triggers from the `apex` directory to your Salesforce org.
1. Update the endpoint URL in `HerokuPoster.cls` to your Heroku app's URL.
1. Add your Heroku app's URL to the Remote Site Settings in Salesforce.

## Posting Chatter data continuously
See the instructions at https://github.com/alouie-sfdc/chatter-data-pump

## Running the Kafka consumer locally
This will use the open source [TextBlob](https://textblob.readthedocs.io) package to perform sentiment analysis on the Chatter data.
1. `pip install -r requirements.txt`
1. `python consumer.py`
1. `CTRL-C` to quit
