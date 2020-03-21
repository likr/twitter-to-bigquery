import json
import time
from google.cloud import bigquery
from google.cloud import language


bq_client = bigquery.Client(project='vdslab-covid19')
nlp_client = language.LanguageServiceClient()


def process(id, text):
    time.sleep(1)
    entities = nlp_client.analyze_entities({
        'content': text,
        'type': language.enums.Document.Type.PLAIN_TEXT,
        'language': 'ja'
    }, encoding_type=language.enums.EncodingType.UTF8)
    sentiment = nlp_client.analyze_sentiment({
        'content': text,
        'type': language.enums.Document.Type.PLAIN_TEXT,
        'language': 'ja'
    }, encoding_type=language.enums.EncodingType.UTF8)
    return {
        'id': id,
        'entities': [entity.name for entity in entities.entities],
        'sentiment': {
            'magnitude': sentiment.document_sentiment.magnitude,
            'score': sentiment.document_sentiment.score,
        }
    }


def main():
    query = '''
SELECT
  id,
  text
FROM
  `vdslab-covid19.twitter.test2`
WHERE
  retweet_count >= 100
ORDER BY
  retweet_count DESC'''
    job = bq_client.query(query, location='asia-northeast1')
    with open('sentiment.json', 'w') as f:
        for id, text in job:
            item = process(id, text)
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
