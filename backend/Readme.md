Prerequisite:

1. Create a service account in GCP that has permission to
- Read/Write a storage bucket in GCP
- Publish and subscribe to pub/sub

2. Download the service account key, rename it as `service-account.json` and put it in the `backend/` folder.

3. Modify config.py, change to values of the following keys to your own
- BUCKET_NAME
- PUBSUB_TOPIC

4. For our initial run, we keep (in config.py) the database connection string and the redis host untouched

5. Make sure docker desktop is started

To inject the initial data to database, run `alembic upgrade head` (With venv activated).  This will create the initial database tables for you.

Start server:
Use the command `docker compose up -d`

However, if docker is not available, we can switch back to the classic way:

1. Start a remote machine, install PostgreSQL and Redis

2. Modify config.py to the corresponding PostgreSQL and Redis host/credential

3. Setup a venv for python, pip install everying, then start the flask server with `flask --app main run` 

