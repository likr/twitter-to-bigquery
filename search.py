import time
from google.cloud import bigquery
from util import convert, get_api


def main():
    client = bigquery.Client('vdslab-covid19')
    table = client.get_table('twitter.test2')
    api = get_api()
    max_id = None
    while True:
        print(max_id)
        tweets = api.search('(コロナ OR covid19 OR 武漢肺炎) min_retweets:10',
                            lang='ja',
                            locale='ja',
                            result_type='recent',
                            count=1000,
                            max_id=max_id)
        if len(tweets) == 0:
            break
        client.insert_rows(table, [convert(status._json) for status in tweets])
        max_id = tweets.max_id
        time.sleep(5)


if __name__ == '__main__':
    main()
