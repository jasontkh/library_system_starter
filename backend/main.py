from datetime import datetime
from uuid import uuid4

import config
import sql_helper
import redis_helper
from database import SessionLocal
from flask import Flask, abort, json, make_response, request
from gcs_helper import CloudStorageHelper
from google.cloud import storage
from google.cloud.pubsub_v1 import PublisherClient
from redis import Redis
import jwt
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, supports_credentials=True)
gcs_helper = CloudStorageHelper(storage.Client.from_service_account_json('./service-account.json'))
publisher = PublisherClient.from_service_account_json('./service-account.json')
redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

# Config CORS, this is a one time configuration
from google.cloud import storage
client = storage.Client.from_service_account_json('./service-account.json')
bucket = client.bucket(config.BUCKET_NAME)
bucket.cors = [
    {
        "origin": ["*"],
        "responseHeader": ["*"],
        "method": ["*"],
        "maxAgeSeconds": 3600
    }
]
bucket.patch()


def store_login_status(response, user, max_age=60 * 60 * 24 * 7):
    # WARNING: Very insecure cookie setting
    # This is just for demo purposes
    # HK Golden had the same security issue back in 200X and people can impose as other users
    # response.set_cookie('user_id', str(user.id), max_age=max_age)

    encoded = jwt.encode({"user_id": user.id}, "secret", algorithm="HS256")

    response.set_cookie('auth_token', encoded, max_age=max_age)

    return response


def check_login_status(request):
    auth_token = request.cookies.get('auth_token')
    if not auth_token:
        return False, None, "Not logged in"
    
    user_id = jwt.decode(auth_token, "secret", algorithms=["HS256"]).get("user_id")

    if not user_id:
        return False, None, "Not logged in"
    user = sql_helper.get_user(SessionLocal(), user_id)
    if not user:
        return False, None, "User does not exist"
    return True, user, "OK"


def get_user():
    auth_token = request.cookies.get('auth_token')
    user_id = jwt.decode(auth_token, "secret", algorithms=["HS256"]).get("user_id")
    user = sql_helper.get_user(SessionLocal(), user_id)
    return user


@app.before_request
def check_login():

    if request.method == "OPTIONS":
        return

    whitelisted_paths = [
        '/login',
        '/signup',
        '/health',
        '/'
    ]
    if request.path in whitelisted_paths:
        return

    success, user, message = check_login_status(request)
    if not success:
        return make_response({"success": False, "message": message}, 400)

# @app.after_request
# def add_cors_header(response):
#     response.headers.add('Access-Control-Allow-Credentials', True)
#     return response

@app.route('/')
@app.route('/health')
def health_check():
    return make_response("OK", 200)


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    if not data.get('username'):
        return make_response({"success": False, "message": "Missing username"}, 400)

    if not data.get('password'):
        return make_response({"success": False, "message": "Password must not be empty"}, 400)

    success, user, message = sql_helper.create_user(SessionLocal(), data['username'], data['password'])

    if not success:
        return make_response({"success": False, "message": message}, 400)

    return make_response({"success": True, "message": None}, 200)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('username'):
        return make_response({"success": False, "message": "Missing username"}, 400)

    if not data.get('password'):
        return make_response({"success": False, "message": "Password must not be empty"}, 400)

    success, user, message = sql_helper.login(SessionLocal(), data['username'], data['password'])

    if not success:
        return make_response({"success": False, "message": message}, 400)

    response = make_response({"success": True, "message": None}, 200)
    store_login_status(response, user)

    return response

@app.route('/document/<int:document_id>', methods=['GET'])
def get_document(document_id):
    document = sql_helper.get_document(SessionLocal(), document_id)
    if not document:
        return make_response({"success": False, "message": "Document does not exist"}, 400)
    
    return make_response({
        "success": True,
        "document": {
            "id": document.id,
            "title": document.title,
            "image_url": gcs_helper.get_signed_url(document.bucket_id, document.blob_id, "GET"),
        }
    }, 200)

@app.route('/documents', methods=['GET'])
def list_documents():
    user = get_user()
    documents = sql_helper.list_documents(SessionLocal(), user.id)
    documents = [
        {
            "id": document.id,
            "title": document.title,
            "image_url": gcs_helper.get_signed_url(document.bucket_id, document.blob_id, "GET"),
        }
        for document in documents
    ]
    return make_response({"success": True, "documents": documents}, 200)

@app.route('/related_documents/<int:document_id>', methods=['GET'])
def list_related_documents(document_id):
    related_docs = redis_helper.get_related_documents(redis, document_id)
    documents = []
    session = SessionLocal()
    for related_doc in related_docs:
        doc = sql_helper.get_document(session, related_doc[0])
        if doc:
            documents.append({
                "id": doc.id,
                "title": doc.title,
                "image_url": gcs_helper.get_signed_url(doc.bucket_id, doc.blob_id, "GET"),
            })

    return make_response({"success": True, "documents": documents}, 200)

@app.route('/request_upload_url', methods=['POST'])
def upload_document():
    user = get_user()
    data = request.get_json()
    bucket_id, blob_id = config.BUCKET_NAME, str(uuid4())
    title = data.get('title', blob_id)

    document = sql_helper.create_document(SessionLocal(), title, bucket_id, blob_id, user.id)
    presigned_url = gcs_helper.get_signed_url(bucket_id, blob_id, 'PUT')

    return make_response({
        "success": True,
        "message": "OK",
        "document_id": document.id,
        "presigned_url": presigned_url}, 200)


@app.route('/notify_upload_complete', methods=['POST'])
def notify_upload_complete():
    data = request.get_json()
    document_id = data.get('document_id')
    if not document_id:
        return make_response({"success": False, "message": "Missing document_id"}, 400)

    document = sql_helper.get_document(SessionLocal(), document_id)

    if not document:
        return make_response({"success": False, "message": "Document does not exist"}, 400)

    sql_helper.update_document(SessionLocal(), document_id)

    publisher.publish(config.PUBSUB_TOPIC, json.dumps({
        "document_id": document_id,
        "bucket_id": document.bucket_id,
        "blob_id": document.blob_id
    }).encode('utf-8'))

    return make_response({"success": True, "message": "OK"}, 200)
