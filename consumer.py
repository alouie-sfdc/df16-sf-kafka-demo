"""
Kafka consumer that does sentiment analysis of Chatter data. It identifies the most
polarizing threads and then posts to them via Heroku Connect.
"""

import kafka_helper
import operator
import os
import psycopg2
import urlparse

from collections import namedtuple
from textblob import TextBlob


class SentimentAnalyzer(object):

    feed_item_stats = dict()

    def kafka_stream_analysis_loop(self):
        """
        Endless loop that reads from the Kafka stream and does sentiment
        analysis of each message. Aggregates the results into averages for
        each thread.
        """
        consumer = kafka_helper.get_kafka_consumer(topic='chatter')

        for message in consumer:
            print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                                  message.offset, message.key,
                                                  message.value))
            blob = TextBlob(message.value['Body'])

            # Keep running averages of the most polarizing threads (in the future, we could also keep track
            # of posters and parentIds).
            feed_item_id = message.value['FeedItemId']
            if feed_item_id not in self.feed_item_stats:
                self.feed_item_stats[feed_item_id] = dict(total_polarity=0, num_times=0)

            current_stat = self.feed_item_stats[feed_item_id]
            current_stat['total_polarity'] += blob.sentiment.polarity
            current_stat['num_times'] += 1
            current_stat['average'] = current_stat['total_polarity'] / current_stat['num_times']

    def get_most_negative_and_positive(self):
        """
        Returns a namedtuple containing the most negative and positive threads.
        """

        def sort_function(x):
            # Give the rankings a higher/lower weight if they have at least
            # 1 feed item + 3 comments.
            item = operator.itemgetter(1)(x)
            value = item['average']
            if item['num_times'] >= 4:
                if item['average'] > 0:
                    value += 1
                elif item['average'] < 0:
                    value -= 1
            return value

        sorted_items = sorted(self.feed_item_stats.items(), key=sort_function)
        Extremes = namedtuple('Extremes', ['negative', 'positive'])
        return Extremes(negative=sorted_items[0], positive=sorted_items[-1])

    def write_results_to_db(self, dbconn):
        """
        Inserts comments for the most negative and postitive threads into a Postgres
        database that's assumed to be synced to Salesforce via Heroku Connect.
        """
        extremes = self.get_most_negative_and_positive()

        negative_body = "Hello people. This was the most negative thread. Sentiment score: {}".format(extremes.negative[1]['average'])
        positive_body = "Hello people. This was the most positive thread. Sentiment score: {}".format(extremes.positive[1]['average'])

        with conn, conn.cursor() as cursor:
            for body in [(negative_body, extremes.negative[0]),
                         (positive_body, extremes.positive[0])]:
                cursor.execute(
                    """INSERT INTO salesforce.feedcomment(commentbody, feeditemid)
                       VALUES(%s, %s);""",
                    body
                )
                print body


# Posgres configuration.
urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

if __name__ == '__main__':
    analyzer = SentimentAnalyzer()
    try:
        analyzer.kafka_stream_analysis_loop()
    except KeyboardInterrupt:
        analyzer.write_results_to_db(conn)
        exit()
