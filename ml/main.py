from google.cloud import pubsub_v1
import redis
import pickle
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity
from google.cloud import storage
import os
import json

topic_name = "projects/bold-network-380012/topics/ocr-project"
subscription_name = 'projects/bold-network-380012/subscriptions/ocr-project-sub'

with open("vectorizer.pkl", "rb") as fp:
    vectorizer = pickle.load(fp)

with open("doc_vec.pkl", "rb") as fp:
    old_doc_vectors = pickle.load(fp)

with open("doc_id.pkl", "rb") as fp:
    old_doc_ids = pickle.load(fp)

if not os.path.exists("temp2/"):
    os.mkdir("temp2/")

storage_client = storage.Client.from_service_account_json("service-account.json")


def callback(message):
    print(message)
    # Something like {"blob_id": "a77aaa67-1753-4200-b0f4-44720e997bdc", "bucket_id": "demo-bucket-dododo2", "document_id": 15}
    message_data = message.data.decode("utf8")                              # Bytes to string
    message_obj = json.loads(message_data)                                  # String to Dictionary

    bucket_id = message_obj['bucket_id']                                    # Extract values from dictionary
    blob_id = message_obj['blob_id']
    doc_id = message_obj['document_id']

    bucket = storage_client.bucket(bucket_id)                               # Download pdf according to pubsub message
    blob = bucket.blob(blob_id)
    blob.download_to_filename(f'temp2/{doc_id}.pdf')

    reader = PdfReader(f'temp2/{doc_id}.pdf')                               # Read the words from pdf
    all_pages = []
    for page in reader.pages:
        all_pages.append(page.extract_text())
    doc_string = " ".join(all_pages)

    new_doc_vec = vectorizer.transform([doc_string])                        # Convert words to vector
    scores = cosine_similarity(old_doc_vectors, new_doc_vec).reshape(-1)    # Compare with old docs, generate similarity score

    mapping = {k: v for k, v in zip(old_doc_ids, scores)}                   # Group similarity scores with old doc ids

    r = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, db=0)

    r.zadd(doc_id, mapping)

    for old_doc_id, score in mapping.items():
        r.zadd(old_doc_id, {doc_id: score})

    r.close()
    message.ack()
    print("Done!")


with pubsub_v1.SubscriberClient.from_service_account_file("service-account.json") as subscriber:
    future = subscriber.subscribe(subscription_name, callback)
    try:
        future.result()
    except KeyboardInterrupt:
        future.cancel()
