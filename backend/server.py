import sql_helper
from database import SessionLocal
from flask import Flask, json, make_response, request, abort
from gcs_helper import CloudStorageHelper
from google.cloud import storage
from google.cloud.pubsub_v1 import PublisherClient
import config

app = Flask(__name__)
gcs_helper = CloudStorageHelper(storage.Client())
publisher = PublisherClient()


def store_login_status(response, user, max_age=60 * 60 * 24 * 7):
    # WARNING: Very insecure cookie setting
    # This is just for demo purposes
    # HK Golden had the same security issue back in 200X and people can impose as other users
    response.set_cookie('user_id', str(user.id), max_age=max_age)
    return response


def check_login_status(request):
    user_id = request.cookies.get('user_id')
    if not user_id:
        return False, None, "Not logged in"
    user = sql_helper.get_user(SessionLocal(), user_id)
    if not user:
        return False, None, "User does not exist"
    return True, user, "OK"


def require_login(func):
    def wrapper(*args, **kwargs):
        success, _, message = check_login_status(request)
        if not success:
            return make_response({"success": False, "message": message}, 400)
        return func(*args, **kwargs)
    return wrapper


def check_login():
    whitelisted_paths = [
        '/login',
        '/signup',
        '/health',
        '/'
    ]
    if request.path not in whitelisted_paths:
        return

    success, user, message = check_login_status(request)
    if not success:
        return make_response({"success": False, "message": message}, 400)


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


@require_login
@app.route('/documents', methods=['GET'])
def list_documents():
    success, user, message = check_login_status(request)
    if not success:
        return make_response({"success": False, "message": message}, 400)

    documents = sql_helper.list_documents(SessionLocal(), user.id)
    documents = [
        {
            "id": document.id,
            "title": document.title,
            "gcs_uri": document.gcs_uri,
            "image_url": gcs_helper.get_signed_url(document.gcs_uri),
        }
        for document in documents
    ]
    return make_response({"success": True, "documents": documents}, 200)


@app.route('/document', methods=['POST'])
def upload_document():
    success, user, message = check_login_status(request)
    if not success:
        return make_response({"success": False, "message": message}, 400)

    file = request.files.get('file')

    if not file:
        return make_response({"success": False, "message": "Missing file"}, 400)

    gcs_blob = gcs_helper.upload_file(config.BUCKET_NAME, file.stream.read())
    gcs_uri = f'gs://{gcs_blob.bucket.name}/{gcs_blob.name}'
    sql_helper.create_document(SessionLocal(), file.filename, gcs_uri, user.id)
    publisher.publish(config.PUBSUB_TOPIC, gcs_uri.encode('utf-8'))
    return make_response({"success": True, "message": "OK"}, 200)
